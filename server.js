const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));


/* =========================================================
   KNOWLEDGE BASE
   ========================================================= */

const knowledgePath = path.join(__dirname, "knowledge");

const knowledgeFiles = [
  "company.md",
  "products.md",
  "ingredients.md",
  "policies.md",
  "faq.md",
  "customer-guidance.md"
];

const knowledgeBase = {};

for (const file of knowledgeFiles) {

  const filePath = path.join(knowledgePath, file);

  try {

    knowledgeBase[file] = fs.readFileSync(
      filePath,
      "utf8"
    );

  } catch (error) {

    console.error(`Could not load ${file}:`, error.message);

    knowledgeBase[file] = "";

  }

}

console.log(
  `Loaded ${knowledgeFiles.length} Soft Flower knowledge files.`
);


/* =========================================================
   APPROVED PRODUCT DATA
   ========================================================= */

const products = {

  goldenHour: {
    name: "Golden Hour Serum",
    category: "Facial Serum",
    price: "₹1,499",
    description:
      "Lightweight facial serum that supports a healthy-looking radiant complexion.",
    ingredients: [
      "Hyaluronic Acid",
      "Niacinamide",
      "Vitamin E"
    ],
    usage:
      "Apply a small amount to clean skin before moisturizer, morning or evening."
  },

  softBloom: {
    name: "SOFT Bloom Oil",
    category: "Facial Oil",
    price: "₹1,799",
    description:
      "Nourishing facial oil that complements a moisturizing skincare routine.",
    ingredients: [
      "Jojoba Oil",
      "Squalane",
      "Vitamin E"
    ],
    usage:
      "Apply a few drops after serum or moisturizer."
  },

  midnightCream: {
    name: "Midnight Cream",
    category: "Moisturizer",
    price: "₹1,699",
    description:
      "Rich moisturizer designed for evening skincare.",
    ingredients: [
      "Ceramides",
      "Squalane",
      "Hyaluronic Acid"
    ],
    usage:
      "Apply to clean skin as the final step of an evening routine."
  }

};


/* =========================================================
   GENERAL APPROVED INFORMATION
   ========================================================= */

const approvedCategories = [
  "Facial Serums",
  "Facial Oils",
  "Moisturizers",
  "Cleansers",
  "Body Care",
  "Hair Care"
];

const approvedShipping =
  "Standard delivery generally takes 3–7 business days. Delivery times may vary depending on location.";

const approvedReturns =
  "Unopened and unused products may be eligible for return within 7 days. Opened or used products may not qualify.";

const medicalResponse =
  "Soft Flower products are not documented as treatments or cures for medical conditions. For medical concerns, please consult an appropriate healthcare professional.";

const unavailableResponse =
  "That information is not currently available in the Soft Flower knowledge base.";


/* =========================================================
   TEXT NORMALIZATION
   ========================================================= */

function normalize(text) {

  return String(text || "")
    .toLowerCase()
    .replace(/[^\w\s₹.-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

}


/* =========================================================
   PRODUCT DETECTION
   ========================================================= */

function detectProduct(text) {

  const message = normalize(text);

  if (
    message.includes("golden hour") ||
    message.includes("serum")
  ) {
    return products.goldenHour;
  }

  if (
    message.includes("soft bloom") ||
    message.includes("bloom oil") ||
    message.includes("facial oil")
  ) {
    return products.softBloom;
  }

  if (
    message.includes("midnight") ||
    message.includes("cream") ||
    message.includes("moisturizer")
  ) {
    return products.midnightCream;
  }

  return null;
}


/* =========================================================
   INTENT DETECTION
   ========================================================= */

function detectIntent(text) {

  const message = normalize(text);

  if (!message) {
    return "unknown";
  }


  /* Medical */

  if (
    /\bacne\b/.test(message) ||
    /\btreat\b/.test(message) ||
    /\bcure\b/.test(message) ||
    /\bprevent\b/.test(message) ||
    /\bmedical\b/.test(message) ||
    /\bcondition\b/.test(message) ||
    /\beczema\b/.test(message) ||
    /\bdermatitis\b/.test(message)
  ) {
    return "medical";
  }


  /* Sunscreen */

  if (
    message.includes("sunscreen") ||
    message.includes("sun screen") ||
    message.includes("spf")
  ) {
    return "sunscreen";
  }


  /* Product list */

  if (
    message.includes("what products") ||
    message.includes("which products") ||
    message.includes("products do you have") ||
    message.includes("list products") ||
    message.includes("available products")
  ) {
    return "product-list";
  }


  /* All products */

  if (
    message.includes("all three") ||
    message.includes("three products") ||
    message.includes("use all")
  ) {
    return "all-products";
  }


  /* Lightweight */

  if (
    message.includes("lightweight") ||
    message.includes("light routine") ||
    message.includes("simple routine")
  ) {
    return "lightweight";
  }


  /* Nourishing */

  if (
    message.includes("nourishing") ||
    message.includes("nourish") ||
    message.includes("more nourishment")
  ) {
    return "nourishing";
  }


  /* Rich night */

  if (
    message.includes("richer night") ||
    message.includes("rich night") ||
    message.includes("night routine") ||
    message.includes("evening routine") ||
    message.includes("rich moisturizer")
  ) {
    return "rich-night";
  }


  /* Dry skin */

  if (
    message.includes("dry skin") ||
    message.includes("dryness")
  ) {
    return "dry-skin";
  }


  /* Ingredients */

  if (
    message.includes("ingredient") ||
    message.includes("ingredients")
  ) {
    return "ingredients";
  }


  /* Price */

  if (
    message.includes("price") ||
    message.includes("cost") ||
    message.includes("how much") ||
    message.includes("₹")
  ) {
    return "price";
  }


  /* Usage */

  if (
    message.includes("how to use") ||
    message.includes("how do i use") ||
    message.includes("when to use") ||
    message.includes("apply")
  ) {
    return "usage";
  }


  /* Shipping */

  if (
    message.includes("shipping") ||
    message.includes("delivery") ||
    message.includes("deliver") ||
    message.includes("how long")
  ) {
    return "shipping";
  }


  /* Returns */

  if (
    message.includes("return") ||
    message.includes("refund") ||
    message.includes("opened product") ||
    message.includes("used product")
  ) {
    return "returns";
  }


  /* Damaged order */

  if (
    message.includes("damaged") ||
    message.includes("broken") ||
    message.includes("arrived damaged")
  ) {
    return "damaged";
  }


  /* Cancellation */

  if (
    message.includes("cancel") ||
    message.includes("cancellation")
  ) {
    return "cancellation";
  }


  /* Categories */

  if (
    message.includes("categories") ||
    message.includes("category") ||
    message.includes("what do you sell")
  ) {
    return "categories";
  }


  /* Greetings */

  if (
    message === "hi" ||
    message === "hello" ||
    message === "hey" ||
    message.includes("good morning") ||
    message.includes("good evening")
  ) {
    return "greeting";
  }


  /* Product-specific general question */

  if (detectProduct(message)) {
    return "product-general";
  }


  return "unknown";
}


/* =========================================================
   FOLLOW-UP CONTEXT
   ========================================================= */

function getLastProduct(history) {

  if (!Array.isArray(history)) {
    return null;
  }

  for (let i = history.length - 1; i >= 0; i--) {

    const item = history[i];

    if (!item || typeof item.content !== "string") {
      continue;
    }

    const product = detectProduct(item.content);

    if (product) {
      return product;
    }

  }

  return null;
}


/* =========================================================
   PRODUCT RESPONSE HELPERS
   ========================================================= */

function productListResponse() {

  return `Soft Flower currently has these documented products:

• ${products.goldenHour.name} — ${products.goldenHour.price}
• ${products.softBloom.name} — ${products.softBloom.price}
• ${products.midnightCream.name} — ${products.midnightCream.price}`;

}


function productIngredientsResponse(product) {

  return `${product.name} contains:

• ${product.ingredients.join("\n• ")}`;

}


function productPriceResponse(product) {

  return `${product.name} is priced at ${product.price}.`;

}


function productUsageResponse(product) {

  return `For ${product.name}:

• ${product.usage}`;

}


/* =========================================================
   ROUTINE RESPONSES
   ========================================================= */

function lightweightResponse() {

  return `For a lightweight routine, Golden Hour Serum is the documented choice.

• ${products.goldenHour.name} — ${products.goldenHour.price}
• Lightweight facial serum
• Use a small amount on clean skin before moisturizer
• Suitable for morning or evening use`;

}


function nourishingResponse() {

  return `For a nourishing routine, SOFT Bloom Oil is the documented choice.

• ${products.softBloom.name} — ${products.softBloom.price}
• Nourishing facial oil
• A richer skincare step
• Apply a few drops after serum or moisturizer`;

}


function richNightResponse() {

  return `For a richer night routine, the documented options are:

1. ${products.softBloom.name} — ${products.softBloom.price}
2. ${products.midnightCream.name} — ${products.midnightCream.price}

• SOFT Bloom Oil is a nourishing facial oil.
• Midnight Cream is a rich evening moisturizer.`;

}


function allProductsRoutineResponse() {

  return `Yes. The knowledge base documents this possible routine:

1. ${products.goldenHour.name}
2. ${products.softBloom.name}
3. ${products.midnightCream.name}`;

}


function drySkinResponse() {

  return `For dry skin, the documented options are:

• ${products.softBloom.name} — a nourishing facial oil
• ${products.midnightCream.name} — a richer evening moisturizer

Golden Hour Serum is the lighter option.`;

}


/* =========================================================
   GENERAL KNOWLEDGE SEARCH
   ========================================================= */

function searchKnowledge(keywords) {

  const results = [];

  for (const [file, content] of Object.entries(knowledgeBase)) {

    const normalizedContent =
      normalize(content);

    let score = 0;

    for (const keyword of keywords) {

      if (
        normalizedContent.includes(
          normalize(keyword)
        )
      ) {
        score++;
      }

    }

    if (score > 0) {

      results.push({
        file,
        score
      });

    }

  }

  return results.sort(
    (a, b) => b.score - a.score
  );

}


/* =========================================================
   AGENT RESPONSE ENGINE
   ========================================================= */

function generateAnswer(userMessage, history = []) {

  const message =
    normalize(userMessage);

  const intent =
    detectIntent(userMessage);

  const currentProduct =
    detectProduct(userMessage);

  const previousProduct =
    getLastProduct(history);

  const product =
    currentProduct || previousProduct;


  /* ===================================================
     MEDICAL GUARDRAIL
     =================================================== */

  if (intent === "medical") {
    return medicalResponse;
  }


  /* ===================================================
     UNSUPPORTED SUNSCREEN
     =================================================== */

  if (intent === "sunscreen") {
    return unavailableResponse;
  }


  /* ===================================================
     GREETING
     =================================================== */

  if (intent === "greeting") {

    return `Hello. I'm the Soft Flower Intelligence Assistant.

I can help with Soft Flower products, ingredients, routines, shipping and returns.`;

  }


  /* ===================================================
     PRODUCT LIST
     =================================================== */

  if (intent === "product-list") {
    return productListResponse();
  }


  /* ===================================================
     ALL THREE PRODUCTS
     =================================================== */

  if (intent === "all-products") {
    return allProductsRoutineResponse();
  }


  /* ===================================================
     ROUTINES
     =================================================== */

  if (intent === "lightweight") {
    return lightweightResponse();
  }

  if (intent === "nourishing") {
    return nourishingResponse();
  }

  if (intent === "rich-night") {
    return richNightResponse();
  }

  if (intent === "dry-skin") {
    return drySkinResponse();
  }


  /* ===================================================
     INGREDIENTS
     =================================================== */

  if (intent === "ingredients") {

    if (product) {
      return productIngredientsResponse(product);
    }

    return `The documented Soft Flower ingredients are:

• ${products.goldenHour.name}: ${products.goldenHour.ingredients.join(", ")}
• ${products.softBloom.name}: ${products.softBloom.ingredients.join(", ")}
• ${products.midnightCream.name}: ${products.midnightCream.ingredients.join(", ")}`;

  }


  /* ===================================================
     PRICE
     =================================================== */

  if (intent === "price") {

    if (product) {
      return productPriceResponse(product);
    }

    return productListResponse();
  }


  /* ===================================================
     USAGE
     =================================================== */

  if (intent === "usage") {

    if (product) {
      return productUsageResponse(product);
    }

    return unavailableResponse;
  }


  /* ===================================================
     SHIPPING
     =================================================== */

  if (intent === "shipping") {
    return approvedShipping;
  }


  /* ===================================================
     RETURNS
     =================================================== */

  if (intent === "returns") {
    return approvedReturns;
  }


  /* ===================================================
     DAMAGED ORDER
     =================================================== */

  if (intent === "damaged") {

    return `If your order arrives damaged, please contact Soft Flower support with your order details and photos of the damage.`;

  }


  /* ===================================================
     CANCELLATION
     =================================================== */

  if (intent === "cancellation") {

    return `Orders can be cancelled before dispatch. After dispatch, cancellation may not be possible.`;

  }


  /* ===================================================
     CATEGORIES
     =================================================== */

  if (intent === "categories") {

    return `Soft Flower's documented categories include:

• ${approvedCategories.join("\n• ")}`;

  }


  /* ===================================================
     PRODUCT GENERAL
     =================================================== */

  if (
    intent === "product-general" &&
    product
  ) {

    return `${product.name}

• ${product.category}
• ${product.price}
• ${product.description}
• Ingredients: ${product.ingredients.join(", ")}`;

  }


  /* ===================================================
     SIMPLE FOLLOW-UP QUESTIONS
     =================================================== */

  if (
    product &&
    (
      message.includes("what is it") ||
      message.includes("tell me more") ||
      message.includes("this product") ||
      message.includes("that product")
    )
  ) {

    return `${product.name}

• ${product.category}
• ${product.price}
• ${product.description}
• Ingredients: ${product.ingredients.join(", ")}
• ${product.usage}`;

  }


  /* ===================================================
     KNOWLEDGE SEARCH FALLBACK
     =================================================== */

  const keywords =
    message
      .split(" ")
      .filter(word => word.length >= 5);

  const matches =
    searchKnowledge(keywords);

  if (matches.length > 0) {

    return `I found related information in the Soft Flower knowledge base, but I don't have enough approved information to answer that question precisely.

Please try asking about Soft Flower products, ingredients, routines, shipping or returns.`;

  }


  /* ===================================================
     FINAL SAFE FALLBACK
     =================================================== */

  return `I can help with Soft Flower products, ingredients, routines, shipping and returns.

I don't currently have enough approved information in the knowledge base to answer that question.`;

}


/* =========================================================
   API
   ========================================================= */

app.post("/api/chat", (req, res) => {

  try {

    const message =
      typeof req.body.message === "string"
        ? req.body.message.trim()
        : "";

    const history =
      Array.isArray(req.body.history)
        ? req.body.history
        : [];


    if (!message) {

      return res.status(400).json({
        error: "Please enter a message."
      });

    }


    const reply =
      generateAnswer(
        message,
        history
      );


    return res.json({
      reply
    });


  } catch (error) {

    console.error(
      "Chat error:",
      error
    );

    return res.status(500).json({
      error:
        "The Soft Flower AI assistant is temporarily unavailable."
    });

  }

});


/* =========================================================
   SERVER
   ========================================================= */

const PORT =
  process.env.PORT || 3000;

app.listen(PORT, () => {

  console.log(
    `Soft Flower AI running at http://localhost:${PORT}`
  );

});
