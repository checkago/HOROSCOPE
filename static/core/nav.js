(function () {
    try {
        document.documentElement.classList.add("js");
    } catch (_) {}

    const btn = document.getElementById("nav-toggle");
    const backdrop = document.getElementById("nav-backdrop");
    const nav = document.getElementById("site-nav");
    if (!btn || !backdrop || !nav) {
        return;
    }

    const mq = window.matchMedia("(max-width: 768px)");

    function close() {
        document.body.classList.remove("js-nav-open");
        btn.setAttribute("aria-expanded", "false");
        backdrop.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    function open() {
        document.body.classList.add("js-nav-open");
        btn.setAttribute("aria-expanded", "true");
        backdrop.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function toggle() {
        if (document.body.classList.contains("js-nav-open")) {
            close();
        } else {
            open();
        }
    }

    btn.addEventListener("click", function () {
        if (!mq.matches) {
            return;
        }
        toggle();
    });

    backdrop.addEventListener("click", close);

    nav.querySelectorAll("a.nav-link").forEach(function (a) {
        a.addEventListener("click", function () {
            if (mq.matches) {
                close();
            }
        });
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            close();
        }
    });

    const onMqChange = function (e) {
        if (!e.matches) {
            close();
        }
    };

    if (typeof mq.addEventListener === "function") {
        mq.addEventListener("change", onMqChange);
    } else if (typeof mq.addListener === "function") {
        mq.addListener(onMqChange);
    }
})();
