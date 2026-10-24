"use strict";
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".category-tab").forEach((button) =>
    button.addEventListener("click", () => {
      document.querySelectorAll(".category-tab").forEach((tab) => {
        const selected = tab === button;
        tab.classList.toggle("selected", selected);
        tab.setAttribute("aria-pressed", String(selected));
      });
      document.querySelectorAll(".product-card").forEach((card) => {
        card.hidden =
          button.dataset.category !== "All Items" &&
          card.dataset.category !== button.dataset.category;
      });
    }),
  );
  document
    .querySelectorAll(".add-offer")
    .forEach((button) =>
      button.addEventListener("click", () =>
        Masarak.addOffer(button, {
          kind: button.dataset.kind,
          item_id: button.dataset.item,
          provider: button.dataset.provider,
        }),
      ),
    );
  async function mutate(button, data) {
    button.disabled = true;
    try {
      await Masarak.api("/api/cart", data);
      window.location.reload();
    } catch (error) {
      Masarak.toast(error.message, true);
      button.disabled = false;
    }
  }
  document
    .querySelectorAll(".cart-remove")
    .forEach((button) =>
      button.addEventListener("click", () =>
        mutate(button, { action: "remove", key: button.dataset.key }),
      ),
    );
  document
    .querySelectorAll(".cart-quantity")
    .forEach((button) =>
      button.addEventListener("click", () =>
        mutate(button, {
          action: "update",
          key: button.dataset.key,
          quantity: Number(button.dataset.quantity),
        }),
      ),
    );
  const checkout = document.querySelector("#demo-checkout");
  checkout?.addEventListener("click", async () => {
    checkout.disabled = true;
    try {
      const result = await Masarak.api("/api/checkout", {});
      const output = document.querySelector("#checkout-result");
      output.textContent = result.message;
      output.hidden = false;
      checkout.hidden = true;
    } catch (error) {
      Masarak.toast(error.message, true);
      checkout.disabled = false;
    }
  });
});
