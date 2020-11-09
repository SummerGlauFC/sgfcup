function ready(fn) {
  if (document.readyState !== "loading") {
    fn()
  } else {
    document.addEventListener("DOMContentLoaded", fn)
  }
}

function isVisible(el) {
  if (el) {
    const {opacity, display} = el.ownerDocument.defaultView.getComputedStyle(el, null)
    return opacity === "1" && display !== "none"
  }
  return false
}

function save_display(el) {
  if (el) {
    const {display} = el.ownerDocument.defaultView.getComputedStyle(el, null)
    if (!el.dataset.hasOwnProperty("savedDisplay") && display !== "none")
      el.dataset.savedDisplay = display
  }
}

function hide(el) {
  if (el) {
    save_display(el)
    el.style.display = "none"
  }
}

function show(el) {
  if (el) {
    const {display} = el.ownerDocument.defaultView.getComputedStyle(el, null)
    // restore old display value
    let disp = el.dataset.savedDisplay || display
    el.style.display = disp === "none" ? "block" : disp
  }
}

function fadeIn(el, s) {
  if (el) {
    el.style.display = "none"
    el.style.transition = `opacity ${s}ms`
    el.style.opacity = "0"
    show(el)
    setTimeout(() => {
      el.style.opacity = "1"
    }, s)
  }
}

function fadeOut(el, s, onlyOpacity = false) {
  if (el) {
    el.style.transition = `opacity ${s}ms`
    el.style.opacity = "0"
    save_display(el)
    setTimeout(() => !onlyOpacity && hide(el), s)
  }
}

function fadeToggle(el, s) {
  if (el) {
    el.style.transition = `opacity ${s}ms`
    if (isVisible(el)) {
      fadeOut(el, s)
    } else {
      fadeIn(el, s)
    }
  }
}


function setupLoginForm(form) {
  const key = document.getElementById("key")
  const password = document.getElementById("password")
  const clearFieldsBtn = document.getElementById("clear-fields")
  const logoutBtn = document.getElementById("logout")
  const loginBtn = document.getElementById("login")
  if (clearFieldsBtn) {
    clearFieldsBtn.addEventListener("click", () => {
      key.value = ""
      password.value = ""
    })
  }
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault()
      logout()
    })
  }
  if (loginBtn) {
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault()
      login()

      // only save logged in if loginBtn is present, i.e. login failed
      if (!document.getElementById("login")) {
        set_dropzone_logged_in(true)
      }
    })
  }
}

function handle_auth_promise(resp) {
  const identification = document.getElementById("identification")

  resp.text().then(
    text => {
      identification.innerHTML = text
      setupLoginForm(identification)
    }
  )
}

function set_dropzone_logged_in(state) {
  if (window.Dropzone) {
    const dropzone = Dropzone.forElement("#my-awesome-dropzone")
    if (dropzone) dropzone.updated_login_form = state
  }
}

function logout() {
  set_dropzone_logged_in(false)
  fetch("/logout" + should_show_clear()).then(handle_auth_promise)
}

function should_show_clear() {
  return window.SHOW_CLEAR ? "" : "?hide_clear"
}

function login() {
  const formData = new FormData()
  formData.append("key", document.getElementById("key").value || "")
  formData.append("password", document.getElementById("password").value || "")

  fetch("/login" + should_show_clear(), {
    method: "post",
    body: formData,
    headers: {
      "X-CSRFToken": window.CSRF_TOKEN
    }
  }).then(handle_auth_promise)
}

function updateLoginForm() {
  const identification = document.getElementById("identification")
  fetch("/login" + should_show_clear()).then(resp => {
    return resp.text()
  }).then(
    text => {
      identification.innerHTML = text
      setupLoginForm(identification)
    }
  )
}

ready(() => {
  const identification = document.getElementById("identification")
  if (identification) setupLoginForm(identification)
})

