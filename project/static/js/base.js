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

function equalHeight(el) {
  if (el) {
    let max = 0
    Array.prototype.forEach.call(el.children, child => {
      const height = child.clientHeight
      max = height > max ? height : max
    })
    Array.prototype.forEach.call(el.children, child => {
      child.style.height = `${max}px`
    })
  }
}

ready(() => {
  const key = document.getElementById("key")
  const password = document.getElementById("password")
  const clearFieldsBtn = document.getElementById("clear-fields")
  if (clearFieldsBtn) {
    clearFieldsBtn.addEventListener("click", () => {
      key.value = ""
      password.value = ""
    })
  }
  const wrapper = document.getElementById("wrapper")
  equalHeight(wrapper)
})

