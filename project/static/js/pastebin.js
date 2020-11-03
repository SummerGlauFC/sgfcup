ready(() => {
  const form = document.getElementById("paste")
  const reset = document.getElementById("reset")
  let reset_btn = null
  if (reset) {
    reset_btn = reset.getElementsByTagName("button")[0]
  }
  const msg = document.getElementById("message")
  const textarea = document.getElementById("body")
  const textarea_commit = document.getElementById("commit_message")

  form.addEventListener("submit", (e) => {
    e.preventDefault()
    fadeOut(textarea, 250)
    fadeOut(textarea_commit, 250)
    fetch(form.action, {
      method: "post",
      body: new FormData(form)
    }).then(res => {
      return res.json()
    }).then(data => {
      if (data.success) {
        msg.innerHTML = `<a href="${data.full_url}">${data.full_url}</a>`
      } else {
        if (data.hasOwnProperty("errors")) {
          msg.innerHTML = `
            <b>Errors:</b> 
            <ul class="messages">
              ${data.errors.map((e) => `<li class="error">${e}</li>`).join("\n")}
            </ul>
          `
        } else {
          msg.innerHTML = `Error: ${data.error}`
        }
      }
      setTimeout(() => {
        fadeIn(msg, 250)
        fadeIn(reset, 500)
      }, 250)
    })
  })
  if (reset_btn) {
    reset_btn.addEventListener("click", (e) => {
      e.preventDefault()
      fadeOut(msg, 250)
      fadeOut(reset, 250)
      setTimeout(() => {
        fadeIn(textarea, 250)
        fadeIn(textarea_commit, 250)
      }, 250)
    })
  }
})