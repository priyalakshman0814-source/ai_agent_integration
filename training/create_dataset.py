import json
import random
from pathlib import Path


# ============================================================
# SOFT FLOWER — SKINCARE / PRODUCT AI DATASET
# ============================================================

random.seed(42)

BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
OUTPUT_DIR = BASE_DIR / "training"


KNOWLEDGE_FILES = [
    "company.md",
    "products.md",
    "ingredients.md",
    "policies.md",
    "faq.md",
    "customer-guidance.md",
]


# ============================================================
# BRAND NORMALIZATION
# ============================================================

def normalize_brand(text):

    replacements = [

        ("WILD FLOWER", "SOFT FLOWER"),
        ("Wild Flower", "SOFT FLOWER"),
        ("wild flower", "SOFT FLOWER"),

        ("Wild Bloom Oil", "SOFT Bloom Oil"),
        ("wild bloom oil", "SOFT Bloom Oil"),

    ]

    for old, new in replacements:

        text = text.replace(
            old,
            new
        )

    return text


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

print()
print("=" * 70)
print("SOFT FLOWER SKINCARE AI DATASET GENERATOR")
print("=" * 70)

print()
print("Loading knowledge base...")


knowledge = {}


for filename in KNOWLEDGE_FILES:

    path = KNOWLEDGE_DIR / filename

    if not path.exists():

        raise FileNotFoundError(
            f"Knowledge file not found:\n{path}"
        )

    content = path.read_text(
        encoding="utf-8"
    )

    knowledge[filename] = normalize_brand(
        content
    )

    print(
        f"  ✓ {filename}"
    )


# ============================================================
# DATASET
# ============================================================

examples = []


def add(user, assistant):

    user = normalize_brand(
        user.strip()
    )

    assistant = normalize_brand(
        assistant.strip()
    )

    if not user or not assistant:
        return

    examples.append({

        "messages": [

            {
                "role": "user",
                "content": user
            },

            {
                "role": "assistant",
                "content": assistant
            }

        ]

    })


def add_conversation(messages):

    normalized = []

    for message in messages:

        normalized.append({

            "role": message["role"],

            "content": normalize_brand(
                message["content"].strip()
            )

        })

    examples.append({

        "messages": normalized

    })


# ============================================================
# STANDARD RESPONSES
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
    "SOFT FLOWER products are not documented as treatments "
    "or cures for medical conditions. For medical concerns, "
    "please consult an appropriate healthcare professional."
)


# ============================================================
# GREETINGS
# ============================================================

greetings = [

    "hi",
    "hii",
    "hello",
    "hey",
    "hi there",
    "hello there",
    "hey there",
    "good morning",
    "good afternoon",
    "good evening",
    "hi soft flower",
    "hello soft flower",
    "hey soft flower",
    "hi assistant",
    "hello assistant",
    "hey assistant"

]


GREETING_RESPONSE = (
    "Hello! I'm the SOFT FLOWER Intelligence Assistant. "
    "How can I help you with skincare or our products?"
)


for question in greetings:

    add(
        question,
        GREETING_RESPONSE
    )


# ============================================================
# PRODUCT DATA
# ============================================================

products = {

    "Golden Hour Serum": {

        "category": "Facial Serum",

        "price": "₹1,499",

        "description": (
            "A lightweight facial serum designed to support "
            "a healthy-looking, radiant complexion."
        ),

        "ingredients": [
            "Hyaluronic Acid",
            "Niacinamide",
            "Vitamin E"
        ],

        "usage": (
            "Apply a small amount to clean skin before "
            "moisturizer, morning or evening."
        ),

        "recommendation": (
            "Customers looking for radiance, lightweight "
            "hydration, or a simple daily serum."
        )

    },


    "SOFT Bloom Oil": {

        "category": "Facial Oil",

        "price": "₹1,799",

        "description": (
            "A nourishing facial oil designed to complement "
            "a moisturizing skincare routine."
        ),

        "ingredients": [
            "Jojoba Oil",
            "Squalane",
            "Vitamin E"
        ],

        "usage": (
            "Apply a few drops after serum or moisturizer."
        ),

        "recommendation": (
            "Customers looking for nourishment, soft-feeling "
            "skin, or a richer skincare step."
        )

    },


    "Midnight Cream": {

        "category": "Moisturizer",

        "price": "₹1,699",

        "description": (
            "A rich moisturizer designed for an evening "
            "skincare routine."
        ),

        "ingredients": [
            "Ceramides",
            "Squalane",
            "Hyaluronic Acid"
        ],

        "usage": (
            "Apply to clean skin as the final step of "
            "an evening skincare routine."
        ),

        "recommendation": (
            "Customers looking for rich moisturization, "
            "night-time skincare, or a comfortable final "
            "skincare step."
        )

    }

}


# ============================================================
# PRODUCT LIST
# ============================================================

PRODUCT_LIST_RESPONSE = (
    "SOFT FLOWER currently has these documented products:\n\n"
    "• Golden Hour Serum — ₹1,499\n"
    "• SOFT Bloom Oil — ₹1,799\n"
    "• Midnight Cream — ₹1,699"
)


product_list_questions = [

    "product",
    "products",
    "product list",
    "show products",
    "available products",
    "what products",
    "what products do you have",
    "what products do you sell",
    "which products do you have",
    "which products are available",
    "tell me your products",
    "list your products",
    "show me the products",
    "what can I buy",
    "what can I buy from you",
    "what do you sell",
    "what does SOFT FLOWER sell",
    "what does SOFT FLOWER offer",
    "products available",
    "your products"

]


for question in product_list_questions:

    add(
        question,
        PRODUCT_LIST_RESPONSE
    )


# ============================================================
# PRODUCT-SPECIFIC DATA
# ============================================================

for product_name, product in products.items():

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    general_response = (
        f"{product_name} is a {product['category']}. "
        f"{product['description']} "
        f"The price is {product['price']}."
    )


    general_questions = [

        f"What is {product_name}?",
        f"Tell me about {product_name}",
        f"What is this product {product_name}?",
        f"Can you explain {product_name}?",
        f"What kind of product is {product_name}?",
        f"Tell me more about {product_name}",
        f"Give me information about {product_name}",
        f"What does {product_name} do?",
        f"What should I know about {product_name}?",
        f"Tell me about the {product_name}"

    ]


    for question in general_questions:

        add(
            question,
            general_response
        )


    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price_response = (
        f"{product_name} costs {product['price']}."
    )


    price_questions = [

        f"price {product_name}",
        f"cost {product_name}",
        f"how much {product_name}",
        f"how much is {product_name}",
        f"how much does {product_name} cost",
        f"what is the price of {product_name}",
        f"what does {product_name} cost",
        f"tell me the price of {product_name}",
        f"price for {product_name}",
        f"cost of {product_name}",
        f"what's the price of {product_name}",
        f"how expensive is {product_name}"

    ]


    for question in price_questions:

        add(
            question,
            price_response
        )


    # --------------------------------------------------------
    # INGREDIENTS
    # --------------------------------------------------------

    ingredient_text = ", ".join(
        product["ingredients"]
    )


    ingredient_response = (
        f"{product_name} contains "
        f"{ingredient_text}."
    )


    ingredient_questions = [

        f"ingredients {product_name}",
        f"ingredient {product_name}",
        f"what is in {product_name}",
        f"what are the ingredients in {product_name}",
        f"what does {product_name} contain",
        f"what is inside {product_name}",
        f"list ingredients for {product_name}",
        f"tell me the ingredients of {product_name}",
        f"ingredients of {product_name}",
        f"what ingredients does {product_name} have"

    ]


    for question in ingredient_questions:

        add(
            question,
            ingredient_response
        )


    # --------------------------------------------------------
    # USAGE
    # --------------------------------------------------------

    usage_questions = [

        f"how do I use {product_name}",
        f"how should I use {product_name}",
        f"how to use {product_name}",
        f"how do I apply {product_name}",
        f"how should I apply {product_name}",
        f"when should I use {product_name}",
        f"when do I use {product_name}",
        f"how is {product_name} used",
        f"usage of {product_name}",
        f"tell me how to use {product_name}"

    ]


    for question in usage_questions:

        add(
            question,
            product["usage"]
        )


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    recommendation_questions = [

        f"who is {product_name} for",
        f"who should use {product_name}",
        f"why should I choose {product_name}",
        f"what is {product_name} good for",
        f"when should I choose {product_name}",
        f"would {product_name} suit me",
        f"recommend {product_name}",
        f"should I buy {product_name}"

    ]


    for question in recommendation_questions:

        add(
            question,
            product["recommendation"]
        )


# ============================================================
# SIMPLE SKIN QUESTIONS
# ============================================================

skin_questions = {

    "skin": (
        "I can help with skincare, skin concerns, routines, "
        "ingredients, and SOFT FLOWER products. What would "
        "you like to know about your skin?"
    ),

    "skin care": (
        "I can help with skincare routines, skin concerns, "
        "ingredients, and SOFT FLOWER products. Tell me "
        "what you're looking for."
    ),

    "skincare": (
        "I can help with skincare routines, skin concerns, "
        "ingredients, and SOFT FLOWER products. Tell me "
        "what you're looking for."
    ),

    "dry": (
        "If you're looking for a more nourishing step for "
        "dry-feeling skin, SOFT Bloom Oil may be suitable, "
        "while Midnight Cream is a richer evening moisturizer."
    ),

    "dry skin": (
        "If you're looking for a more nourishing step for "
        "dry-feeling skin, SOFT Bloom Oil may be suitable, "
        "while Midnight Cream is a richer evening moisturizer."
    ),

    "oily skin": (
        "I can help you explore the documented SOFT FLOWER "
        "products for your skincare routine. The knowledge "
        "base does not provide a specific product recommendation "
        "for oily skin."
    ),

    "sensitive skin": (
        "The SOFT FLOWER knowledge base does not provide a "
        "specific recommendation for sensitive skin. "
        "I can provide the documented product information "
        "if you'd like."
    ),

    "combination skin": (
        "The SOFT FLOWER knowledge base does not provide a "
        "specific recommendation for combination skin. "
        "I can provide the documented product information "
        "if you'd like."
    ),

    "normal skin": (
        "The SOFT FLOWER knowledge base does not provide a "
        "specific recommendation for normal skin. "
        "I can provide the documented product information "
        "if you'd like."
    ),

    "routine": (
        "I can help with skincare routines. The documented "
        "three-product routine is:\n\n"
        "1. Golden Hour Serum\n"
        "2. SOFT Bloom Oil\n"
        "3. Midnight Cream"
    ),

    "skincare routine": (
        "The documented three-product routine is:\n\n"
        "1. Golden Hour Serum\n"
        "2. SOFT Bloom Oil\n"
        "3. Midnight Cream"
    ),

    "lightweight": (
        "Golden Hour Serum is the documented lightweight "
        "facial serum option."
    ),

    "light": (
        "Golden Hour Serum is the documented lightweight "
        "facial serum option."
    ),

    "nourishing": (
        "SOFT Bloom Oil is the documented nourishing "
        "facial oil option."
    ),

    "nourish": (
        "SOFT Bloom Oil is the documented nourishing "
        "facial oil option."
    ),

    "night": (
        "Midnight Cream is the documented rich moisturizer "
        "for an evening skincare routine."
    ),

    "nighttime": (
        "Midnight Cream is the documented rich moisturizer "
        "for an evening skincare routine."
    ),

    "evening": (
        "Midnight Cream is the documented rich moisturizer "
        "for an evening skincare routine."
    ),

    "radiance": (
        "Golden Hour Serum is designed to support a "
        "healthy-looking, radiant complexion."
    ),

    "hydration": (
        "Golden Hour Serum is documented for lightweight "
        "hydration."
    ),

    "moisturizer": (
        "Midnight Cream is the documented moisturizer. "
        "It is a rich moisturizer designed for an evening "
        "skincare routine."
    ),

    "serum": (
        "Golden Hour Serum is the documented facial serum. "
        "It is a lightweight serum designed to support a "
        "healthy-looking, radiant complexion."
    ),

    "oil": (
        "SOFT Bloom Oil is the documented facial oil. "
        "It is a nourishing facial oil designed to "
        "complement a moisturizing skincare routine."
    ),

    "cream": (
        "Midnight Cream is the documented moisturizer. "
        "It is a rich cream designed for evening skincare."
    ),

    "ingredient": (
        "I can provide the documented ingredients for "
        "SOFT FLOWER products. Tell me which product "
        "you're asking about."
    ),

    "ingredients": (
        "I can provide the documented ingredients for "
        "SOFT FLOWER products. Tell me which product "
        "you're asking about."
    )

}


for question, answer in skin_questions.items():

    add(
        question,
        answer
    )


# ============================================================
# SALES / OFFERS / BUYING / COMMERCIAL QUESTIONS
# ============================================================

commercial_questions = [

    "sales",
    "sale",
    "offer",
    "offers",
    "discount",
    "discounts",
    "deal",
    "deals",
    "price",
    "prices",
    "cost",
    "buy",
    "buying",
    "purchase",
    "purchasing",
    "order",
    "orders",
    "shop",
    "shopping"

]


for question in commercial_questions:

    add(
        question,
        PRODUCT_LIST_RESPONSE
    )


# ============================================================
# SHIPPING
# ============================================================

shipping_questions = [

    "shipping",
    "delivery",
    "deliver",
    "delivery time",
    "shipping time",
    "how long does delivery take",
    "when will my order arrive",
    "how long will shipping take",
    "when will my package arrive",
    "how many days for delivery"

]


shipping_response = (
    "Standard delivery generally takes 3–7 business days. "
    "Delivery times may vary depending on location."
)


for question in shipping_questions:

    add(
        question,
        shipping_response
    )


# ============================================================
# RETURNS
# ============================================================

return_questions = [

    "return",
    "returns",
    "refund",
    "refunds",
    "can I return this",
    "can I return a product",
    "can I return an opened product",
    "can I return a used product",
    "return policy",
    "how do returns work",
    "how long do I have to return",
    "can I get a refund"

]


return_response = (
    "Unopened and unused products may be eligible for "
    "return within 7 days of delivery. Opened or used "
    "products may not qualify."
)


for question in return_questions:

    add(
        question,
        return_response
    )


# ============================================================
# CANCELLATION
# ============================================================

cancellation_questions = [

    "cancel",
    "cancellation",
    "cancel order",
    "can I cancel my order",
    "how do I cancel my order",
    "can I cancel before dispatch",
    "can I cancel after dispatch"

]


cancellation_response = (
    "Orders may be cancelled before dispatch. Once an "
    "order has been dispatched, cancellation may no "
    "longer be possible."
)


for question in cancellation_questions:

    add(
        question,
        cancellation_response
    )


# ============================================================
# DAMAGED PRODUCT
# ============================================================

damaged_questions = [

    "damaged",
    "broken",
    "damaged product",
    "damaged order",
    "my product arrived damaged",
    "my order arrived damaged",
    "what if my product is damaged"

]


damaged_response = (
    "If your product arrives damaged, please contact "
    "SOFT FLOWER customer support with your order details "
    "and photographs of the damaged product."
)


for question in damaged_questions:

    add(
        question,
        damaged_response
    )


# ============================================================
# MEDICAL / TREATMENT QUESTIONS
# ============================================================

medical_questions = [

    "acne",
    "pimples",
    "pimple",
    "eczema",
    "rosacea",
    "skin disease",
    "skin condition",
    "medical skin problem",
    "does this cure acne",
    "does this treat acne",
    "can this cure pimples",
    "can this treat eczema",
    "will this cure my skin problem",
    "can your products cure skin conditions",
    "does this prevent acne"

]


for question in medical_questions:

    add(
        question,
        MEDICAL_RESPONSE
    )


# ============================================================
# UNSUPPORTED SKINCARE TOPICS
# ============================================================

unsupported_skin_questions = [

    "sunscreen",
    "sun screen",
    "spf",
    "retinol",
    "vitamin c serum",
    "cleanser",
    "toner",
    "eye cream",
    "face wash",
    "face mask",
    "body lotion",
    "hair serum"

]


for question in unsupported_skin_questions:

    add(
        question,
        UNAVAILABLE_RESPONSE
    )


# ============================================================
# OUT-OF-DOMAIN QUESTIONS
#
# These teach the model to stay inside its domain.
# ============================================================

out_of_domain_questions = [

    "machine learning",
    "what is machine learning",
    "artificial intelligence",
    "AI",
    "what is AI",
    "python",
    "write Python code",
    "Java",
    "JavaScript",
    "programming",
    "coding",
    "football",
    "cricket",
    "basketball",
    "politics",
    "politician",
    "president",
    "history",
    "geography",
    "mathematics",
    "math problem",
    "physics",
    "quantum physics",
    "chemistry",
    "astronomy",
    "weather",
    "news",
    "stock market",
    "cryptocurrency",
    "Bitcoin",
    "movie",
    "movies",
    "song",
    "music",
    "recipe",
    "cooking",
    "travel",
    "hotel",
    "flight",
    "programming help",
    "write an essay",
    "write a poem",
    "tell me a joke",
    "joke",
    "who is Elon Musk",
    "who is Taylor Swift",
    "what is the capital of France"

]


for question in out_of_domain_questions:

    add(
        question,
        DOMAIN_RESPONSE
    )


# ============================================================
# OUT-OF-DOMAIN NATURAL SENTENCES
# ============================================================

natural_out_of_domain = [

    "Can you help me with Python?",

    "I want to learn machine learning.",

    "Tell me about football.",

    "Who is the president?",

    "What happened in the news?",

    "Can you write code for me?",

    "Explain quantum physics.",

    "What is Bitcoin?",

    "Help me plan a trip.",

    "Tell me a joke.",

    "What movie should I watch?",

    "Can you help with my math homework?",

    "Tell me about astronomy.",

    "What is artificial intelligence?",

    "Can you write an essay?"

]


for question in natural_out_of_domain:

    add(
        question,
        DOMAIN_RESPONSE
    )


# ============================================================
# FOLLOW-UP CONVERSATIONS
# ============================================================

add_conversation([

    {
        "role": "user",
        "content": "Tell me about Golden Hour Serum."
    },

    {
        "role": "assistant",
        "content": (
            "Golden Hour Serum is a Facial Serum. "
            "It is a lightweight facial serum designed "
            "to support a healthy-looking, radiant complexion. "
            "The price is ₹1,499."
        )
    },

    {
        "role": "user",
        "content": "How much is it?"
    },

    {
        "role": "assistant",
        "content": (
            "Golden Hour Serum costs ₹1,499."
        )
    },

    {
        "role": "user",
        "content": "What is inside it?"
    },

    {
        "role": "assistant",
        "content": (
            "Golden Hour Serum contains Hyaluronic Acid, "
            "Niacinamide, and Vitamin E."
        )
    }

])


add_conversation([

    {
        "role": "user",
        "content": "I have dry skin."
    },

    {
        "role": "assistant",
        "content": (
            "If you're looking for a more nourishing step "
            "for dry-feeling skin, SOFT Bloom Oil may be "
            "suitable, while Midnight Cream is a richer "
            "evening moisturizer."
        )
    },

    {
        "role": "user",
        "content": "What about at night?"
    },

    {
        "role": "assistant",
        "content": (
            "Midnight Cream is the documented rich "
            "moisturizer for an evening skincare routine."
        )
    }

])


add_conversation([

    {
        "role": "user",
        "content": "I want something lightweight."
    },

    {
        "role": "assistant",
        "content": (
            "Golden Hour Serum is the documented "
            "lightweight facial serum option."
        )
    },

    {
        "role": "user",
        "content": "What ingredients does it have?"
    },

    {
        "role": "assistant",
        "content": (
            "Golden Hour Serum contains Hyaluronic Acid, "
            "Niacinamide, and Vitamin E."
        )
    }

])


add_conversation([

    {
        "role": "user",
        "content": "Can I use all three?"
    },

    {
        "role": "assistant",
        "content": (
            "The documented three-product routine is:\n\n"
            "1. Golden Hour Serum\n"
            "2. SOFT Bloom Oil\n"
            "3. Midnight Cream"
        )
    },

    {
        "role": "user",
        "content": "What is the price of the serum?"
    },

    {
        "role": "assistant",
        "content": (
            "Golden Hour Serum costs ₹1,499."
        )
    }

])


add_conversation([

    {
        "role": "user",
        "content": "What is machine learning?"
    },

    {
        "role": "assistant",
        "content": DOMAIN_RESPONSE
    },

    {
        "role": "user",
        "content": "Okay, what is in Midnight Cream?"
    },

    {
        "role": "assistant",
        "content": (
            "Midnight Cream contains Ceramides, "
            "Squalane, and Hyaluronic Acid."
        )
    }

])


# ============================================================
# DUPLICATE REMOVAL
# ============================================================

unique_examples = []

seen = set()


for example in examples:

    key = json.dumps(
        example,
        ensure_ascii=False,
        sort_keys=True
    )

    if key not in seen:

        seen.add(key)

        unique_examples.append(
            example
        )


examples = unique_examples


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(
    examples
)


# ============================================================
# SPLIT
# ============================================================

total = len(examples)

train_end = int(
    total * 0.80
)

validation_end = int(
    total * 0.90
)


train_data = examples[
    :train_end
]

validation_data = examples[
    train_end:validation_end
]

test_data = examples[
    validation_end:
]


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(filename, data):

    path = OUTPUT_DIR / filename

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for item in data:

            file.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                ) + "\n"
            )


write_jsonl(
    "train.jsonl",
    train_data
)

write_jsonl(
    "validation.jsonl",
    validation_data
)

write_jsonl(
    "test.jsonl",
    test_data
)


# ============================================================
# VALIDATION
# ============================================================

def validate(data):

    for index, example in enumerate(data):

        assert "messages" in example

        assert isinstance(
            example["messages"],
            list
        )

        for message in example["messages"]:

            assert message["role"] in {
                "user",
                "assistant"
            }

            assert isinstance(
                message["content"],
                str
            )


validate(train_data)
validate(validation_data)
validate(test_data)


# ============================================================
# REPORT
# ============================================================

print()
print("=" * 70)
print("SKINCARE AI DATASET CREATED")
print("=" * 70)

print()

print(
    f"Total examples:       {total}"
)

print(
    f"Training examples:    {len(train_data)}"
)

print(
    f"Validation examples:  {len(validation_data)}"
)

print(
    f"Test examples:        {len(test_data)}"
)

print()

print(
    "DOMAIN:"
)

print(
    "  ✓ Skincare"
)

print(
    "  ✓ Skin concerns"
)

print(
    "  ✓ Ingredients"
)

print(
    "  ✓ Products"
)

print(
    "  ✓ Routines"
)

print(
    "  ✓ Product usage"
)

print(
    "  ✓ Prices"
)

print(
    "  ✓ Sales / offers"
)

print(
    "  ✓ Orders"
)

print(
    "  ✓ Shipping"
)

print(
    "  ✓ Returns"
)

print()

print(
    "OUTSIDE DOMAIN:"
)

print(
    "  ✓ Rejected"
)

print()

print(
    "Knowledge sources:"
)

for filename in KNOWLEDGE_FILES:

    print(
        f"  ✓ {filename}"
    )

print()

print("=" * 70)
print("READY FOR INSPECTION")
print("=" * 70)