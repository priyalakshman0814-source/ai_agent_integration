const express = require("express");
const cors = require("cors");
const path = require("path");

require("dotenv").config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));


// ============================================================
// SOFT FLOWER RESPONSES
// ============================================================

const DOMAIN_RESPONSE =
  "I'm here to help with SOFT FLOWER products, skincare, skin concerns, ingredients, skincare routines, product usage, orders, shipping, returns, and related beauty and personal-care questions.";

const UNAVAILABLE_RESPONSE =
  "That information is not currently available in the SOFT FLOWER knowledge base.";

const MEDICAL_RESPONSE =
  "I can provide information about SOFT FLOWER products and skincare, but I can't diagnose, treat, cure, or prevent medical conditions. For medical or skin-health concerns, please consult an appropriate healthcare professional.";

const GREETING_RESPONSE =
  "Hi! I'm the SOFT FLOWER Intelligence Assistant. I can help with SOFT FLOWER products, skincare, ingredients, routines, product usage, prices, orders, shipping, and returns.";


// ============================================================
// PRODUCTS
// ============================================================

const PRODUCTS = {
  "golden hour serum": {
    name: "Golden Hour Serum",
    category: "Facial Serum",
    price: "₹1,499",
    description:
      "Golden Hour Serum is a lightweight facial serum designed to support a healthy-looking, radiant complexion.",
    usage:
      "Apply a small amount to clean skin before moisturizer.",
    ingredients: [
      "Hyaluronic Acid",
      "Niacinamide",
      "Vitamin E"
    ]
  },

  "soft bloom oil": {
    name: "SOFT Bloom Oil",
    category: "Facial Oil",
    price: "₹1,799",
    description:
      "SOFT Bloom Oil is a nourishing facial oil designed to complement a moisturizing skincare routine.",
    usage:
      "Apply a few drops after serum or moisturizer.",
    ingredients: [
      "Jojoba Oil",
      "Squalane",
      "Vitamin E"
    ]
  },

  "midnight cream": {
    name: "Midnight Cream",
    category: "Moisturizer",
    price: "₹1,699",
    description:
      "Midnight Cream is a rich moisturizer designed for an evening skincare routine.",
    usage:
      "Apply to clean skin as the final step of an evening skincare routine.",
    ingredients: [
      "Ceramides",
      "Squalane",
      "Hyaluronic Acid"
    ]
  }
};

const UNSUPPORTED_PRODUCTS = [
  "sunscreen",
  "retinol",
  "vitamin c serum",
  "cleanser",
  "toner",
  "eye cream",
  "face wash",
  "face mask",
  "body lotion",
  "hair serum"
];


// ============================================================
// HELPERS
// ============================================================

function normalize(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[’']/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function containsAny(text, terms) {
  return terms.some(term => text.includes(term));
}


// ============================================================
// GREETING
// ============================================================

function isGreeting(text) {
  const greetings = [
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "helo",
    "heloo",
    "good morning",
    "good afternoon",
    "good evening",
    "good night",
    "namaste"
  ];

  return greetings.includes(text);
}


// ============================================================
// MEDICAL
// ============================================================

function isMedicalQuestion(text) {
  return containsAny(text, [
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
    "side effects"
  ]);
}


// ============================================================
// MATH FALSE POSITIVE
// ============================================================

function isMathProductQuestion(text) {
  return (
    /\bproduct of\b/.test(text) ||
    /\bscalar product\b/.test(text) ||
    /\bdot product\b/.test(text) ||
    /\bcross product\b/.test(text) ||
    /\bmultiply\b/.test(text) ||
    /\bmultiplication\b/.test(text) ||
    /\b\d+\s*[*x×]\s*\d+\b/.test(text)
  );
}


// ============================================================
// DOMAIN CHECK
// ============================================================

function isDomainRelevant(text) {

  if (!text) return false;

  if (isGreeting(text)) return true;

  if (isMedicalQuestion(text)) return true;

  if (isMathProductQuestion(text)) return false;

  const contextPhrases = [
    "dry skin",
    "oily skin",
    "sensitive skin",
    "skin concern",
    "for my skin",
    "my skin",
    "my skincare",
    "skin care",
    "skincare routine",
    "night routine",
    "evening routine",
    "morning routine",
    "something lightweight",
    "something light",
    "lightweight routine",
    "richer routine",
    "rich night routine",
    "all three products",
    "all three",
    "damaged product",
    "damaged order",
    "product usage",
    "product information",
    "ingredient list",
    "personal care",
    "beauty products"
  ];

  if (containsAny(text, contextPhrases)) {
    return true;
  }

  if (UNSUPPORTED_PRODUCTS.some(product => text.includes(product))) {
    return true;
  }

  if (Object.keys(PRODUCTS).some(product => text.includes(product))) {
    return true;
  }

  const skincareTerms = [
    "skin",
    "skincare",
    "face",
    "dry",
    "oily",
    "sensitive",
    "acne",
    "hydration",
    "moisturizer",
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
    "lightweight",
    "light",
    "rich",
    "richer",
    "night",
    "morning",
    "nourishing",
    "nourishment",
    "product",
    "products"
  ];

  const commercialTerms = [
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
    "order",
    "orders",
    "shipping",
    "delivery",
    "return",
    "returns",
    "refund",
    "refunds",
    "cancel",
    "cancellation"
  ];

  const words = new Set(text.match(/\b[a-zA-Z]+\b/g) || []);

  if (skincareTerms.some(term => words.has(term))) {
    return true;
  }

  if (commercialTerms.some(term => words.has(term))) {
    return true;
  }

  return false;
}


// ============================================================
// PRODUCT LOOKUP
// ============================================================

function findProduct(text) {

  if (text.includes("golden hour")) {
    return PRODUCTS["golden hour serum"];
  }

  if (
    text.includes("soft bloom") ||
    text.includes("bloom oil")
  ) {
    return PRODUCTS["soft bloom oil"];
  }

  if (text.includes("midnight")) {
    return PRODUCTS["midnight cream"];
  }

  return null;
}


// ============================================================
// PRODUCT LIST
// ============================================================

function productListResponse() {
  return (
    "SOFT FLOWER currently has these products in the knowledge base:\n\n" +
    "• Golden Hour Serum — ₹1,499\n" +
    "• SOFT Bloom Oil — ₹1,799\n" +
    "• Midnight Cream — ₹1,699"
  );
}


// ============================================================
// PRODUCT RESPONSE
// ============================================================

function productResponse(product, text) {

  if (
    text.includes("price") ||
    text.includes("pricing") ||
    text.includes("cost") ||
    text.includes("how much")
  ) {
    return `${product.name} costs ${product.price}.`;
  }

  if (
    text.includes("ingredient") ||
    text.includes("ingredients")
  ) {
    return (
      `The key ingredients in ${product.name} are: ` +
      product.ingredients.join(", ") +
      "."
    );
  }

  if (
    text.includes("use") ||
    text.includes("usage") ||
    text.includes("apply") ||
    text.includes("application")
  ) {
    return `${product.name}: ${product.usage}`;
  }

  return (
    `${product.name} is a ${product.category.toLowerCase()}.\n\n` +
    `${product.description}\n\n` +
    `Price: ${product.price}`
  );
}


// ============================================================
// SKIN GUIDANCE
// ============================================================

function skinGuidance(text) {

  if (text.includes("dry") && text.includes("skin")) {
    return (
      "SOFT Bloom Oil may be suitable if you're looking for " +
      "a more nourishing step in your routine, while Midnight " +
      "Cream is designed as a richer moisturizer for evening use."
    );
  }

  if (
    text.includes("lightweight") ||
    text.includes("something light") ||
    text === "light"
  ) {
    return (
      "Golden Hour Serum may be a good fit because it is " +
      "described as a lightweight serum."
    );
  }
  if (
  text.includes("nourishing") &&
  (text.includes("routine") || text.includes("skincare"))
) {
  return (
    "SOFT Bloom Oil may be suitable if you're looking for " +
    "a more nourishing step in your routine."
  );
}
  if (
    (text.includes("rich") || text.includes("richer")) &&
    (text.includes("night") || text.includes("routine"))
  ) {
    return (
      "Midnight Cream is designed as a rich evening moisturizer " +
      "and a comfortable final step of an evening skincare routine."
    );
  }

  if (
    text.includes("night routine") ||
    text.includes("evening routine")
  ) {
    return (
      "Midnight Cream is designed for an evening skincare routine " +
      "and can be used as the final step after cleansing."
    );
  }

  return null;
}


// ============================================================
// ROUTINE
// ============================================================

function routineResponse(text) {

  if (
    text.includes("all three") ||
    text === "routine" ||
    text.includes("skincare routine")
  ) {
    return (
      "A possible routine using all three SOFT FLOWER products is:\n\n" +
      "1. Golden Hour Serum\n" +
      "2. SOFT Bloom Oil\n" +
      "3. Midnight Cream\n\n" +
      "Golden Hour Serum is used before moisturizer, " +
      "SOFT Bloom Oil can be applied after serum or moisturizer, " +
      "and Midnight Cream is designed as the final step of an " +
      "evening routine."
    );
  }

  return null;
}


// ============================================================
// POLICIES
// ============================================================

function policyResponse(text) {

  if (
    text.includes("shipping") ||
    text.includes("delivery")
  ) {
    return (
      "Standard delivery generally takes 3–7 business days. " +
      "Delivery times may vary depending on location."
    );
  }

  if (
    text.includes("return") ||
    text.includes("returns")
  ) {
    return (
      "Customers may request a return within 7 days of delivery. " +
      "Products must be unopened and unused. Products that have " +
      "been opened or used may not qualify for return."
    );
  }

  if (text.includes("refund")) {
    return (
      "Approved refunds are processed after the returned product " +
      "has been inspected. Refund processing time may vary " +
      "depending on the payment method."
    );
  }

  if (
    text.includes("cancel") ||
    text.includes("cancellation")
  ) {
    return (
      "Orders may be cancelled before they are dispatched. " +
      "Once an order has been dispatched, cancellation may " +
      "no longer be possible."
    );
  }

  if (text.includes("damaged")) {
    return (
      "If a product arrives damaged, contact SOFT FLOWER " +
      "customer support with your order details and photographs " +
      "of the damaged product."
    );
  }

  return null;
}


// ============================================================
// SALES
// ============================================================

function salesResponse(text) {

  if (
    containsAny(text, [
      "sale",
      "sales",
      "offer",
      "offers",
      "discount",
      "deal",
      "deals"
    ])
  ) {
    return (
      "The SOFT FLOWER knowledge base does not currently document " +
      "a specific sale, offer, discount, or deal."
    );
  }

  return null;
}


// ============================================================
// ORDER
// ============================================================

function orderResponse(text) {

  if (text.includes("order")) {
    return (
      "The knowledge base contains information about order " +
      "shipping, returns, refunds, cancellation, and damaged " +
      "products. For a specific order-status question, the " +
      "information is not currently available in the SOFT FLOWER " +
      "knowledge base."
    );
  }

  return null;
}


// ============================================================
// GENERAL QUESTIONS
// ============================================================

function generalIngredientResponse(text) {

  if (
    text === "ingredient" ||
    text === "ingredients" ||
    text === "what are the ingredients" ||
    text === "what ingredients do you have"
  ) {
    return (
      "The documented SOFT FLOWER products contain these key ingredients:\n\n" +
      "• Golden Hour Serum: Hyaluronic Acid, Niacinamide, Vitamin E\n" +
      "• SOFT Bloom Oil: Jojoba Oil, Squalane, Vitamin E\n" +
      "• Midnight Cream: Ceramides, Squalane, Hyaluronic Acid"
    );
  }

  return null;
}

function generalPriceResponse(text) {

  if (
    text === "price" ||
    text === "pricing" ||
    text === "cost" ||
    text === "how much"
  ) {
    return (
      "The current documented SOFT FLOWER product prices are:\n\n" +
      "• Golden Hour Serum — ₹1,499\n" +
      "• SOFT Bloom Oil — ₹1,799\n" +
      "• Midnight Cream — ₹1,699"
    );
  }

  return null;
}

function purchaseResponse(text) {

  if (
    text === "buy" ||
    text === "purchase" ||
    text === "shop"
  ) {
    return productListResponse();
  }

  return null;
}


// ============================================================
// MAIN ANSWER ENGINE
// ============================================================

function generateAnswer(userMessage) {

  const text = normalize(userMessage);

  if (!text) {
    return "Please enter a question about SOFT FLOWER.";
  }

  // Domain gate first
  if (!isDomainRelevant(text)) {
    return DOMAIN_RESPONSE;
  }

  // Medical safety
  if (isMedicalQuestion(text)) {
    return MEDICAL_RESPONSE;
  }

  // Unsupported products
  if (
    UNSUPPORTED_PRODUCTS.some(product =>
      text.includes(product)
    )
  ) {
    return UNAVAILABLE_RESPONSE;
  }

  // Greeting
  if (isGreeting(text)) {
    return GREETING_RESPONSE;
  }

  // General skin
  if (
    text === "skin" ||
    text === "skincare" ||
    text === "skin care"
  ) {
    return (
      "SOFT FLOWER's skincare information covers products, " +
      "ingredients, routines, product usage, and skin-related " +
      "guidance available in the knowledge base.\n\n" +
      "The documented products are:\n" +
      "• Golden Hour Serum — ₹1,499\n" +
      "• SOFT Bloom Oil — ₹1,799\n" +
      "• Midnight Cream — ₹1,699"
    );
  }

  // Product
  const product = findProduct(text);

  if (product) {
    return productResponse(product, text);
  }

  // Product list
  if (
    text === "product" ||
    text === "products" ||
    text === "what products do you have" ||
    text === "what products do you sell" ||
    text === "what do you sell"
  ) {
    return productListResponse();
  }

  // Ingredients
  let response = generalIngredientResponse(text);

  if (response) return response;

  // Prices
  response = generalPriceResponse(text);

  if (response) return response;

  // Skin guidance
  response = skinGuidance(text);

  if (response) return response;

  // Routine
  response = routineResponse(text);

  if (response) return response;

  // Policies
  response = policyResponse(text);

  if (response) return response;

  // Sales
  response = salesResponse(text);

  if (response) return response;

  // Purchase
  response = purchaseResponse(text);

  if (response) return response;

  // Orders
  response = orderResponse(text);

  if (response) return response;

  // Simple standalone product types
  if (text === "serum") {
    return "Golden Hour Serum — ₹1,499";
  }

  if (text === "cream") {
    return "Midnight Cream — ₹1,699";
  }

  if (text === "oil") {
    return "SOFT Bloom Oil — ₹1,799";
  }

  // Relevant but undocumented
  return UNAVAILABLE_RESPONSE;
}


// ============================================================
// HEALTH
// ============================================================

app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "SOFT FLOWER Intelligence Assistant",
    generatedBy: "soft-flower-knowledge"
  });
});


// ============================================================
// CHAT API
// ============================================================

app.post("/api/chat", (req, res) => {

  try {

    const message =
      typeof req.body.message === "string"
        ? req.body.message.trim()
        : "";

    if (!message) {
      return res.status(400).json({
        error: "Message is required."
      });
    }

    console.log("\n========================================");
    console.log("CUSTOMER:", message);

    const reply = generateAnswer(message);

    console.log("GENERATED BY: soft-flower-knowledge");
    console.log("AI:", reply);
    console.log("========================================\n");

    return res.json({
      reply,
      generatedBy: "soft-flower-knowledge"
    });

  } catch (error) {

    console.error("CHAT API ERROR:", error);

    return res.status(500).json({
      error:
        "The SOFT FLOWER Intelligence Assistant is temporarily unavailable."
    });
  }
});


// ============================================================
// ROOT
// ============================================================

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});


// ============================================================
// START
// ============================================================

const PORT = process.env.PORT || 3000;

app.listen(PORT, "0.0.0.0", () => {

  console.log("\n========================================");
  console.log("SOFT FLOWER WEBSITE SERVER");
  console.log("========================================");
  console.log(`Website running on port ${PORT}`);
  console.log("Python AI: DISABLED FOR PUBLIC DEPLOYMENT");
  console.log("Gemini: DISABLED");
  console.log("SOFT FLOWER knowledge engine: ENABLED");
  console.log("========================================\n");

});