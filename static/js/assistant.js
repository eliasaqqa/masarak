"use strict";
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#chat-form");
  const input = document.querySelector("#chat-input");
  const messages = document.querySelector("#chat-messages");
  let busy = false;
  function bubble(text, type) {
    const node = document.createElement("div");
    node.className = `chat-bubble ${type}`;
    if (type === "assistant") {
      const label = document.createElement("span");
      label.className = "chat-label";
      label.textContent = "✧ Masarak Assistant";
      node.append(label);
    }
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    node.append(paragraph);
    const timestamp = document.createElement("small");
    timestamp.textContent = "Just now";
    node.append(timestamp);
    messages.append(node);
    messages.scrollTop = messages.scrollHeight;
    return node;
  }
  async function send(message) {
    if (busy || !message.trim()) return;
    busy = true;
    form.querySelector("button").disabled = true;
    bubble(message, "user");
    input.value = "";
    messages.setAttribute("aria-busy", "true");
    try {
      const response = await Masarak.api("/api/assistant", { message });
      const node = bubble(response.reply, "assistant");
      for (const offer of response.recommendations) {
        const card = document.createElement("div");
        card.className = "chat-recommendation";
        const title = document.createElement("strong");
        title.textContent = offer.title;
        const detail = document.createElement("p");
        detail.textContent = `${offer.provider} · SAR ${offer.price.toFixed(2)} · ${offer.delivery}`;
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "+ Add to demo cart";
        button.addEventListener("click", () => Masarak.addOffer(button, offer));
        card.append(title, detail, button);
        node.append(card);
      }
      messages.scrollTop = messages.scrollHeight;
    } catch (error) {
      bubble(error.message, "assistant");
    } finally {
      busy = false;
      form.querySelector("button").disabled = false;
      messages.setAttribute("aria-busy", "false");
    }
  }
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    send(input.value.trim());
  });
  document
    .querySelectorAll("[data-prompt]")
    .forEach((button) =>
      button.addEventListener("click", () => send(button.dataset.prompt)),
    );
});
