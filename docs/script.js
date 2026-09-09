const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");
const mobileNavQuery = window.matchMedia("(max-width: 850px)");

function setNavOpen(open, { returnFocus = false } = {}) {
  if (!menuToggle || !siteNav) return;

  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  siteNav.classList.toggle("open", open);
  document.body.classList.toggle("nav-open", open);

  if (open) {
    siteNav.querySelector("a")?.focus();
  } else if (returnFocus) {
    menuToggle.focus();
  }
}

if (menuToggle && siteNav) {
  menuToggle.setAttribute("aria-label", "Open menu");

  menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    setNavOpen(!isOpen);
  });

  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setNavOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && siteNav.classList.contains("open")) {
      setNavOpen(false, { returnFocus: true });
      return;
    }

    if (
      event.key !== "Tab" ||
      !mobileNavQuery.matches ||
      !siteNav.classList.contains("open")
    ) {
      return;
    }

    const focusableItems = [menuToggle, ...siteNav.querySelectorAll("a")];
    const firstItem = focusableItems[0];
    const lastItem = focusableItems[focusableItems.length - 1];

    if (event.shiftKey && document.activeElement === firstItem) {
      event.preventDefault();
      lastItem.focus();
    } else if (!event.shiftKey && document.activeElement === lastItem) {
      event.preventDefault();
      firstItem.focus();
    }
  });

  const handleViewportChange = (event) => {
    if (!event.matches) setNavOpen(false);
  };

  if (mobileNavQuery.addEventListener) {
    mobileNavQuery.addEventListener("change", handleViewportChange);
  } else {
    mobileNavQuery.addListener(handleViewportChange);
  }
}

const tablist = document.querySelector(".menu-tabs");
const tabs = [...document.querySelectorAll(".menu-tab")];
const panels = [...document.querySelectorAll(".menu-panel")];

if (tablist) tablist.setAttribute("aria-orientation", "horizontal");

function activateTab(selectedTab) {
  tabs.forEach((tab) => {
    const active = tab === selectedTab;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
    tab.setAttribute("tabindex", active ? "0" : "-1");
  });

  panels.forEach((panel) => {
    const active = panel.dataset.panel === selectedTab.dataset.category;
    panel.hidden = !active;
    panel.classList.toggle("active", active);
    panel.setAttribute("aria-hidden", String(!active));
  });
}

tabs.forEach((tab, index) => {
  const category = tab.dataset.category;
  const panel = panels.find(
    (candidate) => candidate.dataset.panel === category
  );

  tab.type = "button";
  tab.id = `menu-tab-${category}`;
  tab.setAttribute("aria-controls", `menu-panel-${category}`);
  tab.setAttribute("tabindex", tab.classList.contains("active") ? "0" : "-1");

  if (panel) {
    panel.id = `menu-panel-${category}`;
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("aria-labelledby", tab.id);
    panel.setAttribute("tabindex", "0");
    panel.setAttribute(
      "aria-hidden",
      String(!tab.classList.contains("active"))
    );
  }

  tab.addEventListener("click", () => activateTab(tab));

  tab.addEventListener("keydown", (event) => {
    let nextIndex;

    if (event.key === "ArrowRight") {
      nextIndex = (index + 1) % tabs.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (index - 1 + tabs.length) % tabs.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = tabs.length - 1;
    } else {
      return;
    }

    event.preventDefault();
    tabs[nextIndex].focus();
    activateTab(tabs[nextIndex]);
  });
});

const form = document.querySelector(".contact-form");

if (form) {
  const formMessage = form.querySelector(".form-message");
  const emailInput = form.elements.email;

  formMessage?.setAttribute("aria-atomic", "true");

  emailInput?.addEventListener("input", () => {
    if (formMessage?.classList.contains("success")) {
      formMessage.textContent = "No spam, ever. Just the good stuff.";
      formMessage.classList.remove("success");
    }
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    if (formMessage) {
      formMessage.textContent =
        "You're on the list — see you in your inbox!";
      formMessage.classList.add("success");
    }

    form.reset();
  });
}

const revealElements = [...document.querySelectorAll(".reveal")];
const reducedMotionQuery = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
);
let revealObserver;

function revealAll() {
  revealElements.forEach((element) => element.classList.add("visible"));
  revealObserver?.disconnect();
}

if ("IntersectionObserver" in window && !reducedMotionQuery.matches) {
  revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  revealElements.forEach((element) => revealObserver.observe(element));
} else {
  revealAll();
}

const handleMotionPreference = (event) => {
  if (event.matches) revealAll();
};

if (reducedMotionQuery.addEventListener) {
  reducedMotionQuery.addEventListener("change", handleMotionPreference);
} else {
  reducedMotionQuery.addListener(handleMotionPreference);
}

const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();