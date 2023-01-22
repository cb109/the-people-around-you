// https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function httpPost(url, payload) {
  const csrftoken = getCookie('csrftoken');
  const formData = new FormData();
  for (const key of Object.keys(payload)) {
    const value = payload[key];
    formData.append(key, value);
  }
  return fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken},
    mode: 'same-origin',
    body: formData,
  });
}
