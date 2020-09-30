ready(() => {
  const form = document.getElementById("paste")
  const reset = document.getElementById("reset")
  const reset_btn = reset.getElementsByTagName("button")[0]
  const msg = document.getElementById("message")
  const textarea = document.getElementById("paste_body")
  const wrapper = document.getElementById("wrapper")

  form.addEventListener("submit", (e) => {
    e.preventDefault()
    fadeOut(textarea, 250)
    fetch(form.action, {
      method: "post",
      body: new FormData(form)
    }).then(res => {
      return res.json()
    }).then(data => {
      if (data.success) {
        msg.innerHTML = `<a href="${data.full_url}">${data.full_url}</a>`
      } else {
        msg.innerHTML = `Error: ${data.error}`
      }
      setTimeout(() => {
        fadeIn(msg, 250)
        fadeIn(reset, 500)
        equalHeight(wrapper)
      }, 250)
    })
  })
  reset_btn.addEventListener("click", (e) => {
    e.preventDefault()
    fadeOut(msg, 250)
    fadeOut(reset, 250)
    setTimeout(() => fadeIn(textarea, 250), 250)
    equalHeight(wrapper)
  })
})