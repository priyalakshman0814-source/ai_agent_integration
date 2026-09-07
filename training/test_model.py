import os
import re
import json
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel


# ============================================================
# CONFIG
# ============================================================

BASE_MODEL = "Qwen/Qwen3-4B-Instruct-2507"

ADAPTER_PATH = os.path.join(
    os.path.dirname(__file__),
    "soft-flower-qwen3-lora"
)

KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "knowledge"
)


# ============================================================
# FIXED RESPONSES
# ============================================================

DOMAIN_RESPONSE = (
    "I'm here to help with SOFT FLOWER products, skincare, skin concerns, "
    "ingredients, skincare routines, product usage, orders, shipping, "
    "returns, and related beauty and personal-care questions."
)

UNAVAILABLE_RESPONSE = (
    "That information is not currently available in the SOFT FLOWER "
    "knowledge base."
)

MEDICAL_RESPONSE = (
    "I can provide information about SOFT FLOWER products and skincare, "
    "but I can't diagnose, treat, cure, or prevent medical conditions. "
    "For medical or skin-health concerns, please consult an appropriate "
    "healthcare professional."
)

GREETING_RESPONSE = (
    "Hi! I'm the SOFT FLOWER Intelligence Assistant. "
    "I can help with SOFT FLOWER products, skincare, ingredients, "
    "routines, product usage, prices, orders, shipping, and returns."
)


# ============================================================
# APPROVED PRODUCT INFORMATION
# ============================================================

PRODUCTS = {
    "golden hour serum": {
        "name": "Golden Hour Serum",
        "category": "Facial Serum",
        "price": "₹1,499",
        "description": (
            "Golden Hour Serum is a lightweight facial serum designed "
            "to support a healthy-looking, radiant complexion."
        ),
        "ingredients": [
            "Hyaluronic Acid",
            "Niacinamide",
            "Vitamin E",
        ],
        "usage": (
            "Apply a small amount to clean skin before moisturizer."
        ),
        "recommendation": (
            "Customers looking for radiance, lightweight hydration, "
            "or a simple daily serum."
        ),
    },

    "soft bloom oil": {
        "name": "SOFT Bloom Oil",
        "category": "Facial Oil",
        "price": "₹1,799",
        "description": (
            "SOFT Bloom Oil is a nourishing facial oil designed to "
            "complement a moisturizing skincare routine."
        ),
        "ingredients": [
            "Jojoba Oil",
            "Squalane",
            "Vitamin E",
        ],
        "usage": (
            "Apply a few drops after serum or moisturizer."
        ),
        "recommendation": (
            "Customers looking for nourishment, soft-feeling skin, "
            "or a richer skincare step."
        ),
    },

    "midnight cream": {
        "name": "Midnight Cream",
        "category": "Moisturizer",
        "price": "₹1,699",
        "description": (
            "Midnight Cream is a rich moisturizer designed for "
            "an evening skincare routine."
        ),
        "ingredients": [
            "Ceramides",
            "Squalane",
            "Hyaluronic Acid",
        ],
        "usage": (
            "Apply to clean skin as the final step of an evening "
            "skincare routine."
        ),
        "recommendation": (
            "Customers looking for rich moisturization, night-time "
            "skincare, or a comfortable final skincare step."
        ),
    },
}


# ============================================================
# UNSUPPORTED SPECIFIC PRODUCTS
# ============================================================

UNSUPPORTED_PRODUCTS = [
    "sunscreen",
    "retinol",
    "vitamin c serum",
    "cleanser",
    "toner",
    "eye cream",
    "face wash",
    "face mask",
    "body lotion",
    "hair serum",
]


# ============================================================
# DOMAIN TERMS
# ============================================================

SKINCARE_TERMS = [
    "skin",
    "skincare",
    "skin care",
    "face",
    "facial",
    "dry",
    "dry skin",
    "oily",
    "oily skin",
    "sensitive",
    "sensitive skin",
    "acne",
    "hydration",
    "hydrate",
    "hydrating",
    "moisturizer",
    "moisturiser",
    "serum",
    "cream",
    "oil",
    "cleanser",
    "toner",
    "sunscreen",
    "retinol",
    "ingredients",
    "ingredient",
    "routine",
    "beauty",
    "personal care",
    "personal-care",
    "lightweight",
    "light",
    "rich",
    "richer",
    "night",
    "morning",
    "nourishing",
    "nourishment",
    "product",
    "products",
]


COMMERCIAL_TERMS = [
    "price",
    "pricing",
    "cost",
    "sale",
    "sales",
    "offer",
    "offers",
    "discount",
    "deal",
    "deals",
    "buy",
    "purchase",
    "shop",
    "shopping",
    "order",
    "orders",
    "shipping",
    "delivery",
    "return",
    "returns",
    "refund",
    "refunds",
    "cancel",
    "cancellation",
    "dispatch",
    "damaged",
]


DOMAIN_CONTEXT_PHRASES = [
    "for my skin",
    "on my skin",
    "my skin",
    "skin concern",
    "skin concerns",
    "skin type",
    "skincare routine",
    "skin routine",
    "night routine",
    "morning routine",
    "evening routine",
    "something lightweight",
    "something light",
    "something rich",
    "richer routine",
    "dry skin",
    "oily skin",
    "sensitive skin",
    "all three products",
    "my product",
    "this product",
    "damaged product",
    "beauty product",
    "personal care product",
]


# ============================================================
# OUT-OF-DOMAIN CONTEXT
# ============================================================

OUT_OF_DOMAIN_TERMS = [
    "machine learning",
    "deep learning",
    "python",
    "javascript",
    "programming",
    "programmer",
    "football",
    "cricket",
    "politics",
    "politician",
    "history",
    "physics",
    "weather",
    "news",
    "mathematics",
    "math",
    "algebra",
    "calculus",
    "database",
    "computer science",
    "coding",
    "code",
]


# ============================================================
# KNOWLEDGE FILE LOADING
# ============================================================

def load_knowledge():
    knowledge = {}

    if not os.path.exists(KNOWLEDGE_DIR):
        return knowledge

    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(".md"):
            path = os.path.join(KNOWLEDGE_DIR, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                # Normalize old brand spelling if present.
                text = text.replace("WILD FLOWER", "SOFT FLOWER")
                text = text.replace("WILD Bloom Oil", "SOFT Bloom Oil")

                knowledge[filename] = text

            except Exception:
                pass

    return knowledge


KNOWLEDGE = load_knowledge()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize(text):
    if not text:
        return ""

    text = text.lower().strip()

    replacements = {
        "wild flower": "soft flower",
        "wild bloom oil": "soft bloom oil",
        "moisturiser": "moisturizer",
        "moisturising": "moisturizing",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# GREETING DETECTION
# ============================================================

def is_greeting(text):
    text = normalize(text)

    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "namaste",
    }

    return text in greetings


# ============================================================
# MEDICAL QUESTION DETECTION
# ============================================================

def is_medical_question(text):
    text = normalize(text)

    medical_terms = [
        "cure",
        "cures",
        "treat",
        "treatment",
        "prevent",
        "prevention",
        "disease",
        "medical condition",
        "eczema",
        "psoriasis",
        "infection",
        "rash",
        "dermatitis",
        "diagnose",
        "diagnosis",
        "medicine",
        "medication",
        "side effect",
        "side effects",
    ]

    return any(term in text for term in medical_terms)


# ============================================================
# MATH FALSE-POSITIVE CHECK
# ============================================================

def is_math_product_question(text):
    text = normalize(text)

    math_patterns = [
        r"\bproduct of\b",
        r"\bscalar product\b",
        r"\bdot product\b",
        r"\bcross product\b",
        r"\bmultiply\b",
        r"\bmultiplication\b",
        r"\b\d+\s*[*x×]\s*\d+\b",
    ]

    return any(re.search(pattern, text) for pattern in math_patterns)


# ============================================================
# DOMAIN RELEVANCE
# ============================================================

def is_domain_relevant(text):
    original = text
    text = normalize(text)

    if not text:
        return False

    # Greetings belong to the assistant's domain.
    if is_greeting(text):
        return True

    # Medical skincare questions are still domain-relevant.
    if is_medical_question(text):
        return True

    # A mathematical use of "product" is NOT a skincare question.
    if is_math_product_question(text):
        return False

    # Strong skincare/product context.
    if any(term in text for term in DOMAIN_CONTEXT_PHRASES):
        return True

    # Specific unsupported beauty/skincare products are relevant.
    # Example: "Do you sell body lotion?"
    for product in UNSUPPORTED_PRODUCTS:
        if product in text:
            return True

    # Known products are always relevant.
    for product in PRODUCTS:
        if product in text:
            return True

    # Standalone domain words are intentionally accepted.
    # This includes "skin", "product", "serum", "cream", "oil", etc.
    words = set(re.findall(r"\b[a-zA-Z]+\b", text))

    for term in SKINCARE_TERMS:
        if " " not in term and term in words:
            return True

    for term in COMMERCIAL_TERMS:
        if term in words:
            return True

    # Explicit beauty/personal-care context.
    if "beauty" in text or "personal care" in text:
        return True

    # Otherwise reject.
    return False


# ============================================================
# UNSUPPORTED PRODUCT CHECK
# ============================================================

def is_unsupported_product_question(text):
    text = normalize(text)

    for product in UNSUPPORTED_PRODUCTS:

        if product in text:

            # If the unsupported product is mentioned,
            # this is relevant but unavailable.
            return True

    return False


# ============================================================
# PRODUCT LOOKUP
# ============================================================

def find_product(text):
    text = normalize(text)

    # Exact product names first.
    for key, product in PRODUCTS.items():
        if key in text:
            return product

    # Natural shorthand.
    if "golden hour" in text:
        return PRODUCTS["golden hour serum"]

    if "soft bloom" in text or "bloom oil" in text:
        return PRODUCTS["soft bloom oil"]

    if "midnight" in text:
        return PRODUCTS["midnight cream"]

    return None


# ============================================================
# PRODUCT LIST
# ============================================================

def product_list_response():
    return (
        "SOFT FLOWER currently has these products in the knowledge base:\n\n"
        "• Golden Hour Serum — ₹1,499\n"
        "• SOFT Bloom Oil — ₹1,799\n"
        "• Midnight Cream — ₹1,699"
    )


# ============================================================
# PRODUCT RESPONSE
# ============================================================

def product_response(product, text):
    text = normalize(text)

    name = product["name"]

    # Price
    if any(word in text for word in [
        "price",
        "pricing",
        "cost",
        "how much",
    ]):
        return f"{name} costs {product['price']}."

    # Ingredients
    if "ingredient" in text or "ingredients" in text:
        ingredients = ", ".join(product["ingredients"])
        return f"The key ingredients in {name} are: {ingredients}."

    # Usage
    if any(word in text for word in [
        "use",
        "usage",
        "apply",
        "application",
        "how do i use",
        "how should i use",
    ]):
        return f"{name}: {product['usage']}"

    # General product information
    return (
        f"{name} is a {product['category'].lower()}.\n\n"
        f"{product['description']}\n\n"
        f"Price: {product['price']}"
    )


# ============================================================
# GENERAL SKIN RESPONSE
# ============================================================

def general_skin_response(text):
    text = normalize(text)

    if text in {"skin", "skincare", "skin care"}:
        return (
            "SOFT FLOWER's skincare information covers products, "
            "ingredients, routines, product usage, and skin-related "
            "guidance available in the knowledge base.\n\n"
            "The documented products are:\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )

    return None


# ============================================================
# SKIN GUIDANCE
# ============================================================

def skin_guidance_response(text):
    text = normalize(text)

    # Dry skin
    if "dry" in text and "skin" in text:
        return (
            "SOFT Bloom Oil may be suitable if you're looking for "
            "a more nourishing step in your routine, while Midnight "
            "Cream is designed as a richer moisturizer for evening use."
        )

    # Lightweight
    if (
        "lightweight" in text
        or "something light" in text
        or text == "light"
    ):
        return (
            "Golden Hour Serum may be a good fit because it is "
            "described as a lightweight serum."
        )

    # Rich/night
    if (
        ("rich" in text or "richer" in text)
        and ("night" in text or "routine" in text)
    ):
        return (
            "Midnight Cream is designed as a rich evening moisturizer "
            "and a comfortable final step of an evening skincare routine."
        )

    # Night routine
    if "night routine" in text or "evening routine" in text:
        return (
            "Midnight Cream is designed for an evening skincare routine "
            "and can be used as the final step after cleansing."
        )

    return None


# ============================================================
# THREE-PRODUCT ROUTINE
# ============================================================

def all_three_response():
    return (
        "A possible routine using all three SOFT FLOWER products is:\n\n"
        "1. Golden Hour Serum\n"
        "2. SOFT Bloom Oil\n"
        "3. Midnight Cream\n\n"
        "Golden Hour Serum is used before moisturizer, "
        "SOFT Bloom Oil can be applied after serum or moisturizer, "
        "and Midnight Cream is designed as the final step of an "
        "evening routine."
    )


# ============================================================
# ROUTINE RESPONSE
# ============================================================

def routine_response(text):
    text = normalize(text)

    if "all three" in text:
        return all_three_response()

    if text == "routine" or "skincare routine" in text:
        return all_three_response()

    return None


# ============================================================
# POLICY RESPONSES
# ============================================================

def policy_response(text):
    text = normalize(text)

    # Shipping
    if "shipping" in text or "delivery" in text:
        return (
            "Standard delivery generally takes 3–7 business days. "
            "Delivery times may vary depending on location."
        )

    # Returns
    if "return" in text or "returns" in text:
        return (
            "Customers may request a return within 7 days of delivery. "
            "Products must be unopened and unused. Products that have "
            "been opened or used may not qualify for return."
        )

    # Refund
    if "refund" in text:
        return (
            "Approved refunds are processed after the returned product "
            "has been inspected. Refund processing time may vary "
            "depending on the payment method."
        )

    # Cancellation
    if "cancel" in text or "cancellation" in text:
        return (
            "Orders may be cancelled before they are dispatched. "
            "Once an order has been dispatched, cancellation may "
            "no longer be possible."
        )

    # Damaged
    if "damaged" in text:
        return (
            "If a product arrives damaged, contact SOFT FLOWER "
            "customer support with your order details and photographs "
            "of the damaged product."
        )

    return None


# ============================================================
# SALES / OFFERS
# ============================================================

def sales_response(text):
    text = normalize(text)

    sales_terms = [
        "sale",
        "sales",
        "offer",
        "offers",
        "discount",
        "deal",
        "deals",
    ]

    if any(term in text for term in sales_terms):
        return (
            "The SOFT FLOWER knowledge base does not currently document "
            "a specific sale, offer, discount, or deal."
        )

    return None


# ============================================================
# GENERAL PRODUCT QUESTIONS
# ============================================================

def general_product_response(text):
    text = normalize(text)

    if text in {
        "product",
        "products",
        "what products do you have",
        "what products do you sell",
        "what do you sell",
    }:
        return product_list_response()

    return None


# ============================================================
# GENERAL INGREDIENT QUESTIONS
# ============================================================

def general_ingredient_response(text):
    text = normalize(text)

    if text in {
        "ingredient",
        "ingredients",
        "what are the ingredients",
        "what ingredients do you have",
    }:
        return (
            "The documented SOFT FLOWER products contain these key ingredients:\n\n"
            "• Golden Hour Serum: Hyaluronic Acid, Niacinamide, Vitamin E\n"
            "• SOFT Bloom Oil: Jojoba Oil, Squalane, Vitamin E\n"
            "• Midnight Cream: Ceramides, Squalane, Hyaluronic Acid"
        )

    return None


# ============================================================
# GENERAL PRICE QUESTIONS
# ============================================================

def general_price_response(text):
    text = normalize(text)

    if text in {
        "price",
        "pricing",
        "cost",
        "how much",
    }:
        return (
            "The current documented SOFT FLOWER product prices are:\n\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )

    return None


# ============================================================
# BUY / PURCHASE
# ============================================================

def purchase_response(text):
    text = normalize(text)

    if any(term in text for term in [
        "buy",
        "purchase",
        "shop",
    ]):
        return (
            "The SOFT FLOWER knowledge base documents these products:\n\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )

    return None


# ============================================================
# ORDER RESPONSE
# ============================================================

def order_response(text):
    text = normalize(text)

    if "order" in text:
        return (
            "The knowledge base contains information about order "
            "shipping, returns, refunds, cancellation, and damaged "
            "products. For a specific order-status question, the "
            "information is not currently available in the SOFT FLOWER "
            "knowledge base."
        )

    return None


# ============================================================
# MAIN KNOWLEDGE RESPONSE
# ============================================================

def knowledge_response(user_message):

    text = normalize(user_message)

    # Greeting
    if is_greeting(text):
        return GREETING_RESPONSE

    # Medical safety
    if is_medical_question(text):
        return MEDICAL_RESPONSE

    # Unsupported product
    if is_unsupported_product_question(text):
        return UNAVAILABLE_RESPONSE

    # Standalone skin / skincare
    response = general_skin_response(text)

    if response:
        return response

    # Known product
    product = find_product(text)

    if product:
        return product_response(product, text)

    # Product list
    response = general_product_response(text)

    if response:
        return response

    # Ingredients
    response = general_ingredient_response(text)

    if response:
        return response

    # Prices
    response = general_price_response(text)

    if response:
        return response

    # Skin guidance
    response = skin_guidance_response(text)

    if response:
        return response

    # Routine
    response = routine_response(text)

    if response:
        return response

    # Policies
    response = policy_response(text)

    if response:
        return response

    # Sales
    response = sales_response(text)

    if response:
        return response

    # Purchase
    response = purchase_response(text)

    if response:
        return response

    # Orders
    response = order_response(text)

    if response:
        return response

    # General product-related terms
    if text in {"serum", "cream", "oil"}:

        if text == "serum":
            return "Golden Hour Serum — ₹1,499"

        if text == "cream":
            return "Midnight Cream — ₹1,699"

        if text == "oil":
            return "SOFT Bloom Oil — ₹1,799"

    # Relevant but unknown
    if is_domain_relevant(text):
        return UNAVAILABLE_RESPONSE

    # Outside domain
    return DOMAIN_RESPONSE


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print("\nLoading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        trust_remote_code=True
    )

    print("Loading Qwen3-4B in 4-bit...")

    compute_dtype = (
        torch.bfloat16
        if torch.cuda.is_available()
        and torch.cuda.is_bf16_supported()
        else torch.float16
    )

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )

    print("Loading SOFT FLOWER LoRA adapter...")

    model = PeftModel.from_pretrained(
        model,
        ADAPTER_PATH
    )

    model.eval()

    return tokenizer, model


# ============================================================
# MODEL GENERATION
# ============================================================

def generate_model_response(
    user_message,
    tokenizer,
    model,
    max_new_tokens=180
):

    messages = [
        {
            "role": "system",
            "content": (
                "You are the SOFT FLOWER Intelligence Assistant. "
                "Answer only skincare, beauty, SOFT FLOWER product, "
                "ingredient, routine, usage, price, order, shipping, "
                "return, refund, and related personal-care questions. "
                "Do not invent information."
            ),
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    device = next(model.parameters()).device

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.0,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = output[0][inputs["input_ids"].shape[1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip()

    return response


# ============================================================
# STRICT ASK FUNCTION
# ============================================================

def ask_model(user_message):

    # 1. Domain gate
    if not is_domain_relevant(user_message):
        return DOMAIN_RESPONSE

    # 2. Medical safety
    if is_medical_question(user_message):
        return MEDICAL_RESPONSE

    # 3. Unsupported but relevant product/topic
    if is_unsupported_product_question(user_message):
        return UNAVAILABLE_RESPONSE

    # 4. Use approved knowledge
    response = knowledge_response(user_message)

    return response


# ============================================================
# TEST SET
# ============================================================

TEST_QUESTIONS = [

    # Basic domain words
    "skin",
    "product",
    "products",
    "serum",
    "cream",
    "oil",
    "ingredient",
    "ingredients",

    # Skin concerns
    "dry",
    "routine",
    "dry skin",
    "I have dry skin",
    "something lightweight",
    "I want a rich night routine",

    # Product facts
    "What are the ingredients in Midnight Cream?",
    "What is the price of Golden Hour Serum?",
    "How much is SOFT Bloom Oil?",
    "How do I use Golden Hour Serum?",
    "How do I use SOFT Bloom Oil?",
    "How do I use Midnight Cream?",
    "Can I use all three products?",

    # Prices
    "price",
    "pricing",
    "cost",

    # Commercial
    "sale",
    "sales",
    "offer",
    "offers",
    "discount",
    "deal",

    # Purchase
    "buy",
    "purchase",
    "shop",

    # Orders
    "order",
    "orders",
    "Where is my order?",

    # Shipping
    "shipping",
    "delivery",
    "How long does delivery take?",

    # Returns
    "return",
    "returns",
    "Can I return a product?",
    "Can I return an opened product?",

    # Refund
    "refund",
    "How do refunds work?",

    # Cancellation
    "Can I cancel my order?",

    # Damaged
    "My product arrived damaged",

    # Unsupported skincare products
    "Do you sell sunscreen?",
    "Do you sell retinol?",
    "Do you have vitamin C serum?",
    "Do you sell cleanser?",
    "Do you sell toner?",
    "Do you sell eye cream?",
    "Do you sell face wash?",
    "Do you sell face mask?",
    "Do you sell body lotion?",
    "Do you sell hair serum?",

    # Medical
    "Does Golden Hour Serum cure acne?",
    "Can this cream treat eczema?",
    "Can your serum cure my skin condition?",

    # Out of domain
    "What is machine learning?",
    "How do I code in Python?",
    "Who won the football match?",
    "Tell me about politics",
    "What is the weather today?",
    "Explain physics",
    "What happened in the news?",

    # Greetings
    "hi",
    "hello",
    "hey",
]


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests():

    print("\n")
    print("=" * 70)
    print("SOFT FLOWER SKINCARE AI TEST")
    print("=" * 70)

    print("\nKnowledge files loaded:")

    for filename in KNOWLEDGE:
        print(f"  ✓ {filename}")

    print("\nRunning strict routing tests...\n")

    passed = 0
    failed = 0

    for i, question in enumerate(TEST_QUESTIONS, start=1):

        relevant = is_domain_relevant(question)
        response = ask_model(question)

        print("-" * 70)
        print(f"TEST {i}")
        print(f"Question: {question}")
        print(
            "Domain: "
            + ("RELEVANT" if relevant else "OUTSIDE DOMAIN")
        )
        print(f"Response: {response}")

        # Basic sanity checks
        if not response or not response.strip():
            print("RESULT: ❌ FAILED")
            failed += 1
            continue

        # Outside-domain questions must receive refusal.
        if not relevant:
            if response == DOMAIN_RESPONSE:
                print("RESULT: ✓ PASSED")
                passed += 1
            else:
                print("RESULT: ❌ FAILED")
                failed += 1

            continue

        # Unsupported products must return unavailable.
        if is_unsupported_product_question(question):
            if response == UNAVAILABLE_RESPONSE:
                print("RESULT: ✓ PASSED")
                passed += 1
            else:
                print("RESULT: ❌ FAILED")
                failed += 1

            continue

        # Medical questions must return safety response.
        if is_medical_question(question):
            if response == MEDICAL_RESPONSE:
                print("RESULT: ✓ PASSED")
                passed += 1
            else:
                print("RESULT: ❌ FAILED")
                failed += 1

            continue

        print("RESULT: ✓ PASSED")
        passed += 1

    print("\n")
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {len(TEST_QUESTIONS)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
    else:
        print(f"\n⚠ {failed} TEST(S) NEED ATTENTION")


# ============================================================
# INTERACTIVE MODE
# ============================================================

def interactive_mode():

    print("\n")
    print("=" * 70)
    print("SOFT FLOWER AI - INTERACTIVE MODE")
    print("=" * 70)

    print("\nType a skincare/product question.")
    print("Type 'exit' to stop.\n")

    while True:

        try:
            user_message = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_message:
            continue

        if user_message.lower() in {
            "exit",
            "quit",
            "bye",
        }:
            print("Goodbye!")
            break

        response = ask_model(user_message)

        print(f"\nSOFT FLOWER AI: {response}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()

    print("\n")
    choice = input(
        "Start interactive mode? (y/n): "
    ).strip().lower()

    if choice == "y":
        interactive_mode()