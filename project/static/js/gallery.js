window.current_page = window.current_page || "1"

function _wr(type) {
  const orig = history[type]
  return function () {
    const rv = orig.apply(this, arguments)
    const e = new Event(type)
    e.arguments = arguments
    e.state = arguments[0]
    window.dispatchEvent(e)
    return rv
  }
}

// patch history to fire pushState events
history.pushState = _wr("pushState")

function addLinkHandlers(el) {
  const links = el.querySelectorAll(".pages a")
  Array.prototype.forEach.call(links, (link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault()
      const {page} = e.target.dataset
      const url = e.target.href
      if (page !== undefined && page !== window.current_page) {
        history.pushState({page, url}, document.title, url)
      }
    })
  })
}

function load_page(page, url) {
  const mainForm = document.getElementById("main_form")
  const main = document.getElementById("main")
  const loader = document.getElementById("loader")

  fadeOut(mainForm, 100, true)
  fadeIn(loader, 100)

  // disable clicking on the hidden contents while it loads
  mainForm.style.pointerEvents = "none"

  fetch(url, {
    headers: {
      "X-AJAX": "true"
    }
  }).then(res => res.text())
    .then(data => {
      // delay so we don't flash the content too fast
      setTimeout(() => {
        fadeOut(loader, 100)
        setTimeout(() => {
          mainForm.style.pointerEvents = "inherit"
          main.innerHTML = data
          if (page)
            window.current_page = page
          addLinkHandlers(document)
          fadeOut(mainForm, 0)
          fadeIn(mainForm, 1000)
        }, 100)
      }, 200)
    })
}

ready(() => {
  const handleEvent = (e) => {
    console.log(e)
    const {page, url} = e.state || {page: "1", url: "."}
    if (page !== window.current_page) {
      load_page(page, url)
    }
  }

  window.addEventListener("popstate", handleEvent)
  window.addEventListener("pushState", handleEvent)
  addLinkHandlers(document)
})