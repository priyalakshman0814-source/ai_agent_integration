import os
import sys
import torch

from flask import Flask, request, jsonify
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_MODEL = "Qwen/Qwen3-4B-Instruct-2507"

ADAPTER_PATH = os.path.join(
    BASE_DIR,
    "training",
    "soft-flower-qwen3-lora"
)

KNOWLEDGE_DIR = os.path.join(
    BASE_DIR,
    "knowledge"
)


# ============================================================
# APP
# ============================================================

app = Flask(__name__)


# ============================================================
# FIXED RESPONSES
# ============================================================

DOMAIN_RESPONSE = (
    "I'm here to help with SOFT FLOWER products, skincare, "
    "skin concerns, ingredients, skincare routines, product "
    "usage, orders, shipping, returns, and related beauty "
    "and personal-care questions."
)

UNAVAILABLE_RESPONSE = (
    "That information is not currently available in the "
    "SOFT FLOWER knowledge base."
)

MEDICAL_RESPONSE = (
    "I can provide information about SOFT FLOWER products "
    "and skincare, but I can't diagnose, treat, cure, or "
    "prevent medical conditions. For medical or skin-health "
    "concerns, please consult an appropriate healthcare "
    "professional."
)

GREETING_RESPONSE = (
    "Hi! I'm the SOFT FLOWER Intelligence Assistant. "
    "I can help with SOFT FLOWER products, skincare, "
    "ingredients, routines, product usage, prices, "
    "orders, shipping, and returns."
)


# ============================================================
# APPROVED PRODUCTS
# ============================================================

PRODUCTS = {
    "golden hour serum": {
        "name": "Golden Hour Serum",
        "category": "Facial Serum",
        "price": "₹1,499",
        "description": (
            "Golden Hour Serum is a lightweight facial serum "
            "designed to support a healthy-looking, radiant complexion."
        ),
        "ingredients": [
            "Hyaluronic Acid",
            "Niacinamide",
            "Vitamin E",
        ],
        "usage": (
            "Apply a small amount to clean skin before moisturizer."
        ),
    },

    "soft bloom oil": {
        "name": "SOFT Bloom Oil",
        "category": "Facial Oil",
        "price": "₹1,799",
        "description": (
            "SOFT Bloom Oil is a nourishing facial oil designed "
            "to complement a moisturizing skincare routine."
        ),
        "ingredients": [
            "Jojoba Oil",
            "Squalane",
            "Vitamin E",
        ],
        "usage": (
            "Apply a few drops after serum or moisturizer."
        ),
    },

    "midnight cream": {
        "name": "Midnight Cream",
        "category": "Moisturizer",
        "price": "₹1,699",
        "description": (
            "Midnight Cream is a rich moisturizer designed "
            "for an evening skincare routine."
        ),
        "ingredients": [
            "Ceramides",
            "Squalane",
            "Hyaluronic Acid",
        ],
        "usage": (
            "Apply to clean skin as the final step of an "
            "evening skincare routine."
        ),
    },
}


# ============================================================
# UNSUPPORTED BUT RELEVANT PRODUCTS
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
    "oily",
    "sensitive",
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
# NORMALIZATION
# ============================================================

def normalize(text):
    if not text:
        return ""

    return (
        str(text)
        .lower()
        .replace("wild flower", "soft flower")
        .replace("wild bloom oil", "soft bloom oil")
        .replace("moisturiser", "moisturizer")
        .strip()
    )


# ============================================================
# GREETING
# ============================================================

def is_greeting(text):
    text = normalize(text)

    return text in {
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


# ============================================================
# MEDICAL
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
# MATH FALSE POSITIVE
# ============================================================

def is_math_product_question(text):
    text = normalize(text)

    math_phrases = [
        "product of",
        "scalar product",
        "dot product",
        "cross product",
        "multiply",
        "multiplication",
    ]

    return any(
        phrase in text
        for phrase in math_phrases
    )


# ============================================================
# DOMAIN DETECTION
# ============================================================

def is_domain_relevant(text):

    text = normalize(text)

    if not text:
        return False

    if is_greeting(text):
        return True

    if is_medical_question(text):
        return True

    if is_math_product_question(text):
        return False

    if any(
        phrase in text
        for phrase in DOMAIN_CONTEXT_PHRASES
    ):
        return True

    for product in UNSUPPORTED_PRODUCTS:
        if product in text:
            return True

    for product in PRODUCTS:
        if product in text:
            return True

    words = set(text.split())

    for term in SKINCARE_TERMS:
        if " " not in term and term in words:
            return True

    for term in COMMERCIAL_TERMS:
        if " " not in term and term in words:
            return True

    return False


# ============================================================
# PRODUCT DETECTION
# ============================================================

def find_product(text):

    text = normalize(text)

    for key, product in PRODUCTS.items():

        if key in text:
            return product

    if "golden hour" in text:
        return PRODUCTS["golden hour serum"]

    if "soft bloom" in text:
        return PRODUCTS["soft bloom oil"]

    if "bloom oil" in text:
        return PRODUCTS["soft bloom oil"]

    if "midnight" in text:
        return PRODUCTS["midnight cream"]

    return None


# ============================================================
# KNOWLEDGE RESPONSES
# ============================================================

def get_knowledge_response(message):

    text = normalize(message)

    # --------------------------------------------------------
    # Greeting
    # --------------------------------------------------------

    if is_greeting(text):
        return GREETING_RESPONSE


    # --------------------------------------------------------
    # Unsupported products
    # --------------------------------------------------------

    for product in UNSUPPORTED_PRODUCTS:

        if product in text:
            return UNAVAILABLE_RESPONSE


    # --------------------------------------------------------
    # Medical
    # --------------------------------------------------------

    if is_medical_question(text):
        return MEDICAL_RESPONSE


    # --------------------------------------------------------
    # Standalone skin
    # --------------------------------------------------------

    if text in {
        "skin",
        "skincare",
        "skin care",
    }:

        return (
            "SOFT FLOWER's skincare information covers "
            "products, ingredients, routines, product usage, "
            "and skin-related guidance available in the "
            "knowledge base.\n\n"

            "The documented products are:\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )


    # --------------------------------------------------------
    # Product list
    # --------------------------------------------------------

    if text in {
        "product",
        "products",
        "what products",
        "what products do you have",
        "what products do you sell",
        "what do you sell",
    }:

        return (
            "SOFT FLOWER currently has these products:\n\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )


    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    product = find_product(text)

    if product:

        if any(
            word in text
            for word in [
                "ingredient",
                "ingredients",
                "inside",
                "made of",
            ]
        ):

            return (
                f"The key ingredients in "
                f"{product['name']} are: "
                + ", ".join(product["ingredients"])
                + "."
            )


        if any(
            word in text
            for word in [
                "price",
                "pricing",
                "cost",
                "how much",
            ]
        ):

            return (
                f"{product['name']} costs "
                f"{product['price']}."
            )


        if any(
            word in text
            for word in [
                "use",
                "usage",
                "apply",
                "application",
            ]
        ):

            return (
                f"{product['name']}: "
                f"{product['usage']}"
            )


        return (
            f"{product['name']} is a "
            f"{product['category'].lower()}.\n\n"
            f"{product['description']}\n\n"
            f"Price: {product['price']}"
        )


    # --------------------------------------------------------
    # Dry skin
    # --------------------------------------------------------

    if (
        "dry skin" in text
        or "skin is dry" in text
        or "skin feels dry" in text
    ):

        return (
            "SOFT Bloom Oil may be suitable if you're "
            "looking for a more nourishing step in your "
            "routine, while Midnight Cream is designed "
            "as a richer moisturizer for evening use."
        )


    # --------------------------------------------------------
    # Lightweight
    # --------------------------------------------------------

    if (
        "lightweight" in text
        or "something light" in text
    ):

        return (
            "Golden Hour Serum may be a good fit because "
            "it is described as a lightweight serum."
        )


    # --------------------------------------------------------
    # Rich night routine
    # --------------------------------------------------------

    if (
        ("rich" in text or "richer" in text)
        and (
            "night" in text
            or "evening" in text
            or "routine" in text
        )
    ):

        return (
            "Midnight Cream is designed as a rich evening "
            "moisturizer and a comfortable final step of "
            "an evening skincare routine."
        )


    # --------------------------------------------------------
    # All three
    # --------------------------------------------------------

    if (
        "all three" in text
        or "three products" in text
        or "use all" in text
        or "use them together" in text
    ):

        return (
            "A possible routine using all three SOFT FLOWER "
            "products is:\n\n"
            "1. Golden Hour Serum\n"
            "2. SOFT Bloom Oil\n"
            "3. Midnight Cream"
        )


    # --------------------------------------------------------
    # Routine
    # --------------------------------------------------------

    if (
        text == "routine"
        or "skincare routine" in text
    ):

        return (
            "A possible routine using all three SOFT FLOWER "
            "products is:\n\n"
            "1. Golden Hour Serum\n"
            "2. SOFT Bloom Oil\n"
            "3. Midnight Cream"
        )


    # --------------------------------------------------------
    # Sales / offers
    # --------------------------------------------------------

    if any(
        term in text
        for term in [
            "sale",
            "sales",
            "offer",
            "offers",
            "discount",
            "deal",
            "deals",
        ]
    ):

        return (
            "The SOFT FLOWER knowledge base does not "
            "currently document a specific sale, offer, "
            "discount, or deal."
        )


    # --------------------------------------------------------
    # Shipping
    # --------------------------------------------------------

    if (
        "shipping" in text
        or "delivery" in text
    ):

        return (
            "Standard delivery generally takes 3–7 "
            "business days. Delivery times may vary "
            "depending on location."
        )


    # --------------------------------------------------------
    # Returns
    # --------------------------------------------------------

    if (
        "return" in text
        or "returns" in text
    ):

        return (
            "Customers may request a return within 7 days "
            "of delivery. Products must be unopened and "
            "unused. Products that have been opened or "
            "used may not qualify for return."
        )


    # --------------------------------------------------------
    # Refund
    # --------------------------------------------------------

    if (
        "refund" in text
        or "refunds" in text
    ):

        return (
            "Approved refunds are processed after the "
            "returned product has been inspected. Refund "
            "processing time may vary depending on the "
            "payment method."
        )


    # --------------------------------------------------------
    # Cancellation
    # --------------------------------------------------------

    if (
        "cancel" in text
        or "cancellation" in text
    ):

        return (
            "Orders may be cancelled before they are "
            "dispatched. Once an order has been dispatched, "
            "cancellation may no longer be possible."
        )


    # --------------------------------------------------------
    # Damaged
    # --------------------------------------------------------

    if "damaged" in text:

        return (
            "If a product arrives damaged, contact SOFT FLOWER "
            "customer support with your order details and "
            "photographs of the damaged product."
        )


    # --------------------------------------------------------
    # General ingredients
    # --------------------------------------------------------

    if text in {
        "ingredient",
        "ingredients",
    }:

        return (
            "The documented SOFT FLOWER products contain "
            "these key ingredients:\n\n"
            "• Golden Hour Serum: Hyaluronic Acid, "
            "Niacinamide, Vitamin E\n"
            "• SOFT Bloom Oil: Jojoba Oil, Squalane, "
            "Vitamin E\n"
            "• Midnight Cream: Ceramides, Squalane, "
            "Hyaluronic Acid"
        )


    # --------------------------------------------------------
    # General price
    # --------------------------------------------------------

    if text in {
        "price",
        "pricing",
        "cost",
    }:

        return (
            "The current documented SOFT FLOWER product "
            "prices are:\n\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )


    # --------------------------------------------------------
    # Buy / purchase
    # --------------------------------------------------------

    if (
        "buy" in text
        or "purchase" in text
        or "shop" in text
    ):

        return (
            "The SOFT FLOWER knowledge base documents "
            "these products:\n\n"
            "• Golden Hour Serum — ₹1,499\n"
            "• SOFT Bloom Oil — ₹1,799\n"
            "• Midnight Cream — ₹1,699"
        )


    # --------------------------------------------------------
    # Order
    # --------------------------------------------------------

    if "order" in text:

        return (
            "The knowledge base contains information about "
            "order shipping, returns, refunds, cancellation, "
            "and damaged products. For a specific order-status "
            "question, the information is not currently "
            "available in the SOFT FLOWER knowledge base."
        )


    # --------------------------------------------------------
    # Known generic skincare words
    # --------------------------------------------------------

    if text == "serum":
        return "Golden Hour Serum — ₹1,499"

    if text == "cream":
        return "Midnight Cream — ₹1,699"

    if text == "oil":
        return "SOFT Bloom Oil — ₹1,799"


    # --------------------------------------------------------
    # Relevant but unavailable
    # --------------------------------------------------------

    if is_domain_relevant(text):
        return UNAVAILABLE_RESPONSE


    # --------------------------------------------------------
    # Outside domain
    # --------------------------------------------------------

    return DOMAIN_RESPONSE


# ============================================================
# LOAD MODEL
# ============================================================

print("\n" + "=" * 70)
print("SOFT FLOWER AI SERVER")
print("=" * 70)

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    trust_remote_code=True,
)

print("Loading Qwen3-4B...")

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
    ADAPTER_PATH,
)

model.eval()

print("✓ Qwen3-4B loaded")
print("✓ SOFT FLOWER LoRA loaded")


# ============================================================
# API ENDPOINT
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        message = data.get("message", "")

        if not isinstance(message, str):
            message = str(message)

        message = message.strip()

        if not message:

            return jsonify({
                "reply": (
                    "Please ask me about SOFT FLOWER products, "
                    "ingredients, routines, shipping, or returns."
                )
            })


        print("\n" + "-" * 70)
        print("CUSTOMER:", message)


        # ----------------------------------------------------
        # DOMAIN GATE
        # ----------------------------------------------------

        if not is_domain_relevant(message):

            reply = DOMAIN_RESPONSE

            print("ROUTE: OUTSIDE DOMAIN")

            return jsonify({
                "reply": reply,
                "generatedBy": "domain-guardrail",
            })


        # ----------------------------------------------------
        # MEDICAL
        # ----------------------------------------------------

        if is_medical_question(message):

            reply = MEDICAL_RESPONSE

            print("ROUTE: MEDICAL GUARDRAIL")

            return jsonify({
                "reply": reply,
                "generatedBy": "medical-guardrail",
            })


        # ----------------------------------------------------
        # KNOWLEDGE
        # ----------------------------------------------------

        reply = get_knowledge_response(message)

        print("ROUTE: SOFT FLOWER KNOWLEDGE")

        print("RESPONSE:", reply)

        return jsonify({
            "reply": reply,
            "generatedBy": "soft-flower-knowledge",
        })


    except Exception as error:

        print(
            "AI SERVER ERROR:",
            str(error)
        )

        return jsonify({
            "error": (
                "The SOFT FLOWER Intelligence Assistant "
                "is temporarily unavailable."
            )
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "model": "Qwen3-4B-Instruct-2507",
        "adapter": "SOFT FLOWER LoRA",
    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("SOFT FLOWER AI READY")
    print("=" * 70)

    print("\nAPI:")
    print("http://127.0.0.1:5000/chat")

    print("\nHealth:")
    print("http://127.0.0.1:5000/health")

    print("\nPress CTRL+C to stop.\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )