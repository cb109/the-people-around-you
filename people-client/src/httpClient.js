const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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

function _httpRequest(method, url, payload = null) {
  const csrftoken = getCookie('csrftoken');
  const data = {
    method: method,
    headers: {
      'X-CSRFToken': csrftoken,
    },
    mode: 'cors',
  };
  if (payload !== null) {
    const formData = new FormData();
    for (const key of Object.keys(payload)) {
      let value = payload[key];
      const isNamedImageBlobUpload = !!value && !!value.name && value.type.startsWith('image');
      if (isNamedImageBlobUpload) {
        const blob = value;
        formData.append(key, blob, blob.name);
      } else {
        formData.append(key, value);
      }
    }
    data.body = formData;
  }
  return fetch(API_BASE_URL + url, data);
}

export function httpGet(url, query = null) {
  if (query) {
    url += '?' + new URLSearchParams(query).toString();
  }
  return _httpRequest('GET', url);
}

export function httpPost(url, payload) {
  return _httpRequest('POST', url, payload);
}
