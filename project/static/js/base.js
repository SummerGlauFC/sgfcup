function ready(fn) {
  if (document.readyState !== "loading") {
    fn()
  } else {
    document.addEventListener("DOMContentLoaded", fn)
  }
}

function equalHeight(el) {
  let max = 0
  Array.prototype.forEach.call(el.children, child => {
    const height = child.clientHeight
    max = height > max ? height : max
  })
  Array.prototype.forEach.call(el.children, child => {
    child.style.height = `${max}px`
  })
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
  if (wrapper) {
    window.addEventListener("resize", () => equalHeight(wrapper))
    equalHeight(wrapper)
  }
})

