document.addEventListener("DOMContentLoaded", () => {

  /* =====================================================
     MOBILE NAVIGATION
     ===================================================== */

  const menu = document.querySelector(".menu");
  const nav = document.querySelector(".nav");

  if (menu && nav) {

    menu.addEventListener("click", () => {
      nav.classList.toggle("open");
    });

    nav.querySelectorAll("a").forEach((link) => {

      link.addEventListener("click", () => {
        nav.classList.remove("open");
      });

    });

  }


  /* =====================================================
     CHATBOT ELEMENTS
     ===================================================== */

  const messagesBox = document.querySelector(".messages");
  const aiInput = document.getElementById("ai-input");
  const sendButton = document.getElementById("send");

  if (!messagesBox || !aiInput || !sendButton) {
    return;
  }


  let conversationHistory = [];


  /* =====================================================
     CLEAN AI RESPONSE
     ===================================================== */

  function cleanAIText(text) {

    if (!text) {
      return "";
    }

    return text

      // Remove old AI INSIGHT label
      .replace(/\*{0,2}AI INSIGHT\*{0,2}/gi, "")

      // Remove markdown headings
      .replace(/^#{1,6}\s*/gm, "")

      // Remove bold markdown
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/__(.*?)__/g, "$1")

      // Remove italic markdown
      .replace(/\*(.*?)\*/g, "$1")
      .replace(/_(.*?)_/g, "$1")

      // Remove remaining asterisks
      .replace(/\*/g, "")

      // Keep bullets clean
      .replace(/^[-•]\s*/gm, "• ")

      // Remove excessive blank lines
      .replace(/\n{3,}/g, "\n\n")

      .trim();
  }


  /* =====================================================
     ADD MESSAGE
     ===================================================== */

  function addMessage(type, text) {

    const message = document.createElement("div");

    message.className = type;

    message.textContent = text;

    messagesBox.appendChild(message);

    messagesBox.scrollTop = messagesBox.scrollHeight;

    return message;
  }


  /* =====================================================
     ADD AI MESSAGE
     ===================================================== */

  function addAIMessage(text) {

    addMessage(
      "assistant",
      cleanAIText(text)
    );

  }


  /* =====================================================
     GET SELECTED ROUTINE
     ===================================================== */

  function getSelectedRoutine() {

    const selected = document.querySelector(
      'input[name="routine"]:checked'
    );

    return selected
      ? selected.value
      : "";

  }


  /* =====================================================
     GET SELECTED HELP TOPICS
     ===================================================== */

  function getSelectedHelp() {

    return Array.from(
      document.querySelectorAll(
        'input[name="help"]:checked'
      )
    ).map((checkbox) => checkbox.value);

  }


  /* =====================================================
     CLEAR QUICK OPTIONS
     ===================================================== */

  function clearSelections() {

    document
      .querySelectorAll('input[name="routine"]')
      .forEach((radio) => {

        radio.checked = false;

      });


    document
      .querySelectorAll('input[name="help"]')
      .forEach((checkbox) => {

        checkbox.checked = false;

      });

  }


  /* =====================================================
     SEND MESSAGE
     ===================================================== */

  async function sendMessage() {

    const typedMessage =
      aiInput.value.trim();


    const selectedRoutine =
      getSelectedRoutine();


    const selectedHelp =
      getSelectedHelp();


    /*
      Don't send an empty message.
    */

    if (
      !typedMessage &&
      !selectedRoutine &&
      selectedHelp.length === 0
    ) {

      aiInput.focus();

      return;

    }


    /* ===================================================
       BUILD MESSAGE FOR BACKEND
       =================================================== */

    let userMessage =
      typedMessage;


    if (
      !userMessage &&
      selectedRoutine
    ) {

      userMessage =
        selectedRoutine;

    }


    if (
      selectedHelp.length > 0
    ) {

      userMessage +=
        `${userMessage ? "\n" : ""}` +
        `Areas they want help with: ` +
        `${selectedHelp.join(", ")}`;

    }


    /* ===================================================
       MESSAGE SHOWN TO USER
       =================================================== */

    let displayMessage =
      typedMessage;


    if (
      !displayMessage &&
      selectedRoutine
    ) {

      const routineText = {

        "lightweight routine":
          "I'd like a lightweight routine.",

        "nourishing routine":
          "I'd like a nourishing routine.",

        "richer night routine":
          "I'd like a richer night routine."

      };


      displayMessage =
        routineText[selectedRoutine]
        || selectedRoutine;

    }


    if (
      !displayMessage &&
      selectedHelp.length > 0
    ) {

      displayMessage =
        `I'd like help with ` +
        `${selectedHelp.join(" and ").toLowerCase()}.`;

    }


    if (!displayMessage) {

      displayMessage =
        "I'd like help with my Soft Flower routine.";

    }


    /* ===================================================
       SHOW USER MESSAGE
       =================================================== */

    addMessage(
      "user",
      displayMessage
    );


    /* ===================================================
       RESET INPUT
       =================================================== */

    aiInput.value = "";

    aiInput.disabled = true;

    sendButton.disabled = true;

    sendButton.textContent = "…";


    /* ===================================================
       THINKING MESSAGE
       =================================================== */

    const thinking =
      addMessage(
        "thinking",
        "Thinking…"
      );


    /* ===================================================
       CALL LOCAL BACKEND
       =================================================== */

    try {

      const response =
        await fetch(
            "http://localhost:3000/api/chat",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

              message:
                userMessage,

              history:
                conversationHistory

            })

          }
        );


      const data =
        await response.json();


      thinking.remove();


      if (!response.ok) {

        throw new Error(
          data.error ||
          "Chat request failed."
        );

      }


      /* ===============================================
         DISPLAY AI RESPONSE
         =============================================== */

      addAIMessage(
        data.reply
      );


      /* ===============================================
         SAVE CONVERSATION
         =============================================== */

      conversationHistory.push(

        {
          role: "user",
          content: userMessage
        },

        {
          role: "assistant",
          content: data.reply
        }

      );


      /* ===============================================
         CLEAR BUTTON SELECTIONS
         =============================================== */

      clearSelections();


    } catch (error) {

      console.error(
        "Soft Flower AI:",
        error
      );


      thinking.remove();


      addAIMessage(
        "I'm sorry, the Soft Flower Intelligence Assistant is temporarily unavailable."
      );

    }


    /* ===================================================
       RESTORE INPUT
       =================================================== */

    aiInput.disabled = false;

    sendButton.disabled = false;

    sendButton.textContent = "↑";

    aiInput.focus();

  }


  /* =====================================================
     SEND BUTTON
     ===================================================== */

  sendButton.addEventListener(
    "click",
    sendMessage
  );


  /* =====================================================
     ENTER KEY
     ===================================================== */

  aiInput.addEventListener(
    "keydown",
    (event) => {

      if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

      }

    }
  );

});