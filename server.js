// 
const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

const knowledgeFolder = path.join(__dirname, "knowledge");

const knowledgeFiles = [
  "company.md",
  "products.md",
  "ingredients.md",
  "policies.md",
  "faq.md",
  "customer-guidance.md"
];

// Load knowledge base
let knowledgeBase = "";

for (const file of knowledgeFiles) {
  const filePath = path.join(knowledgeFolder, file);

  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, "utf8");

    knowledgeBase += `
===== ${file} =====

${content}
`;
  } else {
    console.warn(`WARNING: Knowledge file not found: ${file}`);
  }
}

console.log(
  `Loaded ${knowledgeFiles.length} SOFT FLOWER knowledge files.`
);


// --------------------------------------------------
// Helpers
// --------------------------------------------------

function normalize(text) {
  return text
    .toLowerCase()
    .replace(/[₹,]/g, "")
    .replace(/[?!.,]/g, "")
    .trim();
}


function containsAny(text, words) {
  return words.some(word => text.includes(word));
}


// --------------------------------------------------
// Product data extracted from approved knowledge base
// --------------------------------------------------

const products = {
  goldenHour: {
    name: "Golden Hour Serum",
    category: "Facial Serum",
    price: "₹1,499",
    description:
      "A lightweight facial serum designed to support a healthy-looking, radiant complexion.",
    recommendedFor: [
      "Radiance",
      "Lightweight hydration",
      "A simple daily serum"
    ],
    usage:
      "Apply a small amount to clean skin before moisturizer.",
    timing:
      "Morning or evening",
    ingredients: [
      "Hyaluronic Acid",
      "Niacinamide",
      "Vitamin E"
    ]
  },

  SOFTBloom: {
    name: "SOFT Bloom Oil",
    category: "Facial Oil",
    price: "₹1,799",
    description:
      "A nourishing facial oil designed to complement a moisturizing skincare routine.",
    recommendedFor: [
      "Nourishment",
      "Soft-feeling skin",
      "A richer skincare step"
    ],
    usage:
      "Apply a few drops after serum or moisturizer.",
    ingredients: [
      "Jojoba Oil",
      "Squalane",
      "Vitamin E"
    ]
  },

  midnight: {
    name: "Midnight Cream",
    category: "Moisturizer",
    price: "₹1,699",
    description:
      "A rich moisturizer designed for an evening skincare routine.",
    recommendedFor: [
      "Rich moisturization",
      "Night-time skincare",
      "A comfortable final skincare step"
    ],
    usage:
      "Apply to clean skin as the final step of an evening skincare routine.",
    ingredients: [
      "Ceramides",
      "Squalane",
      "Hyaluronic Acid"
    ]
  }
};


// --------------------------------------------------
// Local knowledge assistant
// --------------------------------------------------

function generateAnswer(message) {
  const text = normalize(message);

  // Empty message
  if (!text) {
    return "Please enter a question about SOFT FLOWER products, ingredients, routines, shipping, or returns.";
  }


  // -----------------------------------------------
  // Medical / acne questions
  // -----------------------------------------------

  if (
    containsAny(text, [
      "acne",
      "pimple",
      "pimples",
      "eczema",
      "rosacea",
      "medical",
      "cure",
      "treat",
      "treatment",
      "disease",
      "condition"
    ])
  ) {
    return (
      "SOFT FLOWER products are not documented as treatments or cures for medical conditions. " +
      "For medical concerns, please consult an appropriate healthcare professional."
    );
  }


  // -----------------------------------------------
  // Sunscreen
  // -----------------------------------------------

  if (
    containsAny(text, [
      "sunscreen",
      "sun screen",
      "spf"
    ])
  ) {
    return (
      "That information is not currently available in the SOFT FLOWER knowledge base."
    );
  }


  // -----------------------------------------------
  // Product list
  // -----------------------------------------------
if (
  containsAny(text, [
    "skincare",
    "skin care",
    "skin routine",
    "skin",
    "skincare routine",
    "skin care routine",
    "routine help",
    "help with skincare"
  ])
) {
  return "routine";
}

  if (
    containsAny(text, [
      "what products",
      "products do you have",
      "products do you sell",
      "list products",
      "available products",
      "show products"
    ])
  ) {
    return (
      "SOFT FLOWER currently has these documented products:\n\n" +
      "• Golden Hour Serum — ₹1,499\n" +
      "• SOFT Bloom Oil — ₹1,799\n" +
      "• Midnight Cream — ₹1,699"
    );
  }


  // -----------------------------------------------
  // Lightweight routine
  // -----------------------------------------------

  if (
    containsAny(text, [
      "lightweight routine",
      "something lightweight",
      "light routine",
      "lightweight skincare"
    ])
  ) {
    return (
      "For a lightweight routine, Golden Hour Serum is the documented choice.\n\n" +
      "• Golden Hour Serum — ₹1,499\n" +
      "• Lightweight facial serum\n" +
      "• Use a small amount on clean skin before moisturizer\n" +
      "• Suitable for morning or evening use"
    );
  }


  // -----------------------------------------------
  // Nourishing routine
  // -----------------------------------------------

  if (
    containsAny(text, [
      "nourishing routine",
      "nourishing",
      "more nourishment",
      "skin care routine",
      "nourishing skincare"
    ])
  ) {
    return (
      "For a nourishing routine, SOFT Bloom Oil is the documented choice.\n\n" +
      "• SOFT Bloom Oil — ₹1,799\n" +
      "• Nourishing facial oil\n" +
      "• A richer skincare step\n" +
      "• Apply a few drops after serum or moisturizer"
    );
  }


  // -----------------------------------------------
  // Richer night routine
  // -----------------------------------------------

  if (
    containsAny(text, [
      "richer night",
      "rich night",
      "night routine",
      "night skincare",
      "evening routine"
    ])
  ) {
    return (
      "For a richer night routine, the documented options are:\n\n" +
      "• SOFT Bloom Oil — ₹1,799\n" +
      "• Midnight Cream — ₹1,699\n\n" +
      "Midnight Cream is designed as a rich evening moisturizer and final skincare step."
    );
  }


  // -----------------------------------------------
  // Three-product routine
  // -----------------------------------------------

  if (
    containsAny(text, [
      "all three",
      "three products",
      "use all",
      "use them together",
      "use everything together"
    ])
  ) {
    return (
      "Yes. The knowledge base documents this possible routine:\n\n" +
      "1. Golden Hour Serum\n" +
      "2. SOFT Bloom Oil\n" +
      "3. Midnight Cream"
    );
  }


  // -----------------------------------------------
  // Dry skin
  // -----------------------------------------------

  if (
    containsAny(text, [
      "dry skin",
      "skin is dry",
      "dryness"
    ])
  ) {
    return (
      "If you're looking for a more nourishing step, SOFT Bloom Oil may be suitable. " +
      "Midnight Cream is designed as a richer moisturizer for evening use."
    );
  }


  // -----------------------------------------------
  // Golden Hour Serum
  // -----------------------------------------------

  if (
    containsAny(text, [
      "golden hour",
      "golden hour serum"
    ])
  ) {

    if (
      containsAny(text, [
        "ingredient",
        "ingredients",
        "what is inside"
      ])
    ) {
      return (
        "Golden Hour Serum contains:\n\n" +
        "• Hyaluronic Acid\n" +
        "• Niacinamide\n" +
        "• Vitamin E"
      );
    }

    if (
      containsAny(text, [
        "price",
        "cost",
        "how much"
      ])
    ) {
      return "Golden Hour Serum costs ₹1,499.";
    }

    if (
      containsAny(text, [
        "use",
        "usage",
        "apply",
        "how do i use"
      ])
    ) {
      return (
        "Apply a small amount of Golden Hour Serum to clean skin before moisturizer. " +
        "It is recommended for morning or evening use."
      );
    }

    return (
      "Golden Hour Serum is a lightweight facial serum designed to support a healthy-looking, radiant complexion.\n\n" +
      "Price: ₹1,499"
    );
  }


  // -----------------------------------------------
  // SOFT Bloom Oil
  // -----------------------------------------------

  if (
    containsAny(text, [
      "SOFT bloom",
      "SOFT bloom oil"
    ])
  ) {

    if (
      containsAny(text, [
        "ingredient",
        "ingredients",
        "what is inside"
      ])
    ) {
      return (
        "SOFT Bloom Oil contains:\n\n" +
        "• Jojoba Oil\n" +
        "• Squalane\n" +
        "• Vitamin E"
      );
    }

    if (
      containsAny(text, [
        "price",
        "cost",
        "how much"
      ])
    ) {
      return "SOFT Bloom Oil costs ₹1,799.";
    }

    if (
      containsAny(text, [
        "use",
        "usage",
        "apply",
        "how do i use"
      ])
    ) {
      return (
        "Apply a few drops of SOFT Bloom Oil after serum or moisturizer."
      );
    }

    return (
      "SOFT Bloom Oil is a nourishing facial oil designed to complement a moisturizing skincare routine.\n\n" +
      "Price: ₹1,799"
    );
  }


  // -----------------------------------------------
  // Midnight Cream
  // -----------------------------------------------

  if (
    containsAny(text, [
      "midnight",
      "midnight cream"
    ])
  ) {

    if (
      containsAny(text, [
        "ingredient",
        "ingredients",
        "what is inside"
      ])
    ) {
      return (
        "Midnight Cream contains:\n\n" +
        "• Ceramides\n" +
        "• Squalane\n" +
        "• Hyaluronic Acid"
      );
    }

    if (
      containsAny(text, [
        "price",
        "cost",
        "how much"
      ])
    ) {
      return "Midnight Cream costs ₹1,699.";
    }

    if (
      containsAny(text, [
        "use",
        "usage",
        "apply",
        "how do i use"
      ])
    ) {
      return (
        "Apply Midnight Cream to clean skin as the final step of an evening skincare routine."
      );
    }

    return (
      "Midnight Cream is a rich moisturizer designed for an evening skincare routine.\n\n" +
      "Price: ₹1,699"
    );
  }


  // -----------------------------------------------
  // Ingredients in general
  // -----------------------------------------------

  if (
    containsAny(text, [
      "ingredients",
      "ingredient list"
    ])
  ) {
    return (
      "The documented ingredients are:\n\n" +
      "• Golden Hour Serum: Hyaluronic Acid, Niacinamide, Vitamin E\n" +
      "• SOFT Bloom Oil: Jojoba Oil, Squalane, Vitamin E\n" +
      "• Midnight Cream: Ceramides, Squalane, Hyaluronic Acid"
    );
  }


  // -----------------------------------------------
  // Shipping
  // -----------------------------------------------

  if (
    containsAny(text, [
      "shipping",
      "delivery",
      "deliver",
      "how long",
      "delivery time"
    ])
  ) {
    return (
      "Standard delivery generally takes 3–7 business days. " +
      "Delivery times may vary depending on location."
    );
  }


  // -----------------------------------------------
  // Returns
  // -----------------------------------------------

  if (
    containsAny(text, [
      "return",
      "returns",
      "send back",
      "refund"
    ])
  ) {
    return (
      "Customers may request a return within 7 days of delivery.\n\n" +
      "• Products must be unopened and unused.\n" +
      "• Opened or used products may not qualify for return.\n" +
      "• Approved refunds are processed after the returned product has been inspected."
    );
  }


  // -----------------------------------------------
  // Damaged product
  // -----------------------------------------------

  if (
    containsAny(text, [
      "damaged",
      "broken",
      "arrived damaged"
    ])
  ) {
    return (
      "If your product arrives damaged, contact SOFT FLOWER customer support " +
      "with your order details and photographs of the damaged product."
    );
  }


  // -----------------------------------------------
  // Cancellation
  // -----------------------------------------------

  if (
    containsAny(text, [
      "cancel",
      "cancellation"
    ])
  ) {
    return (
      "Orders may be cancelled before they are dispatched. " +
      "Once an order has been dispatched, cancellation may no longer be possible."
    );
  }


  // -----------------------------------------------
  // Categories
  // -----------------------------------------------

  if (
    containsAny(text, [
      "category",
      "categories",
      "what kind of products"
    ])
  ) {
    return (
      "SOFT FLOWER offers beauty and personal care products including:\n\n" +
      "• Facial serums\n" +
      "• Facial oils\n" +
      "• Moisturizers\n" +
      "• Cleansers\n" +
      "• Body care\n" +
      "• Hair care"
    );
  }
// -----------------------------------------------
// Skincare routine help
// -----------------------------------------------

if (
  containsAny(text, [
    "skincare routine",
    "skin care routine",
    "routine help",
    "help with routine",
    "help me with my routine"
  ])
) {
  return (
    "I can help you choose a SOFT FLOWER skincare routine.\n\n" +
    "You can choose:\n\n" +
    "• Lightweight — Golden Hour Serum\n" +
    "• Nourishing — SOFT Bloom Oil\n" +
    "• Richer night — SOFT Bloom Oil + Midnight Cream\n\n" +
    "Tell me which type of routine you're looking for."
  );
}

  // -----------------------------------------------
  // Greeting
  // -----------------------------------------------

  if (
    containsAny(text, [
      "hello",
      "hi",
      "hey",
      "good morning",
      "good evening"
    ])
  ) {
    return (
      "Hello. I'm the SOFT FLOWER Intelligence Assistant. " +
      "How can I help you today?"
    );
  }


  // -----------------------------------------------
  // Unknown question
  // -----------------------------------------------

  return (
    "That information is not currently available in the SOFT FLOWER knowledge base."
  );
}


// --------------------------------------------------
// Chat API
// --------------------------------------------------

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

    const reply = generateAnswer(message);

    res.json({
      reply
    });

  } catch (error) {

    console.error("CHAT ERROR:", error);

    res.status(500).json({
      error:
        "The SOFT FLOWER Intelligence Assistant is temporarily unavailable."
    });

  }

});


// --------------------------------------------------
// Start server
// --------------------------------------------------

const PORT = process.env.PORT || 3000;

app.listen(PORT, "0.0.0.0", () => {

  console.log(
    `SOFT FLOWER AI running on port ${PORT}`
  );

});