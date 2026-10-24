"use strict";
window.Masarak = (() => {
  let timer;
  function toast(message, error = false) {
    const node = document.querySelector("#toast");
    node.textContent = message;
    node.classList.toggle("error", error);
    node.hidden = false;
    clearTimeout(timer);
    timer = setTimeout(() => {
      node.hidden = true;
    }, 4200);
  }
  async function api(path, data) {
    const response = await fetch(path, {
      method: data === undefined ? "GET" : "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]')
          .content,
      },
      credentials: "same-origin",
      body: data === undefined ? undefined : JSON.stringify(data),
    });
    let result;
    try {
      result = await response.json();
    } catch {
      throw new Error("Something went wrong. Please refresh and try again.");
    }
    if (!response.ok) throw new Error(result.error || "Please try again.");
    return result;
  }
  function updateCount(count) {
    document.querySelectorAll(".cart-badge").forEach((node) => {
      node.textContent = count;
      node.hidden = !count;
    });
  }
  async function addOffer(button, offer) {
    if (button.disabled) return;
    button.disabled = true;
    try {
      const cart = await api("/api/cart", { ...offer, quantity: 1 });
      updateCount(cart.count);
      toast("Added to your demo cart.");
    } catch (error) {
      toast(error.message, true);
    } finally {
      button.disabled = false;
    }
  }
  return { toast, api, addOffer, updateCount };
})();

document.addEventListener("DOMContentLoaded", () => {
  const city = document.querySelector("#city");
  try {
    const saved = localStorage.getItem("masarak-city");
    if (["Riyadh", "Jeddah", "Dammam"].includes(saved)) city.value = saved;
  } catch {
    /* Storage is optional in embedded browsers. */
  }
  city.addEventListener("change", () => {
    try {
      localStorage.setItem("masarak-city", city.value);
    } catch {
      /* Keep the selector usable without storage. */
    }
    Masarak.toast(
      `Prototype city set to ${city.value}. Prices remain sample data.`,
    );
  });
  document.querySelectorAll("[data-demo]").forEach((button) =>
    button.addEventListener("click", () => {
      document.querySelector("#demo-message").textContent = button.dataset.demo;
      document.querySelector("#demo-dialog").showModal();
    }),
  );
  const search = document.querySelector("#home-search");
  if (search) {
    const results = document.querySelector("#search-results");
    const features = [
      ["Food", "/food", "Compare restaurant sample offers"],
      ["Grocery / Market", "/grocery", "Find your everyday essentials"],
      ["Ride", "/coming-soon/ride", "Coming soon"],
      ["Hotels", "/coming-soon/hotels", "Coming soon"],
      ["Flights", "/future", "Future features"],
      ["World Cup", "/future", "Future features"],
      ["Wallet", "/wallet", "Demo wallet"],
    ];
    function close() {
      results.hidden = true;
      search.setAttribute("aria-expanded", "false");
    }
    function show() {
      results.replaceChildren();
      const query = search.value.trim().toLowerCase();
      if (!query) {
        close();
        return;
      }
      const matches = features.filter((feature) =>
        feature[0].toLowerCase().includes(query),
      );
      for (const [label, href, description] of matches) {
        const link = document.createElement("a");
        link.href = href;
        const strong = document.createElement("strong");
        strong.textContent = label;
        const caption = document.createElement("small");
        caption.textContent = description;
        link.append(strong, caption);
        results.append(link);
      }
      if (!matches.length) {
        const text = document.createElement("p");
        text.textContent = "No matching features. Try Food or Market.";
        results.append(text);
      }
      results.hidden = false;
      search.setAttribute("aria-expanded", "true");
    }
    search.addEventListener("input", show);
    search.addEventListener("focus", show);
    search.addEventListener("keydown", (event) => {
      if (event.key === "Escape") close();
      if (event.key === "ArrowDown") {
        event.preventDefault();
        results.querySelector("a")?.focus();
      }
      if (event.key === "Enter") results.querySelector("a")?.click();
    });
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".search-wrap")) close();
    });
    document.addEventListener("keydown", (event) => {
      if (
        event.key === "/" &&
        !["INPUT", "TEXTAREA", "SELECT"].includes(
          document.activeElement.tagName,
        )
      ) {
        event.preventDefault();
        search.focus();
      }
    });
  }
});
