/*
Variables
*/
var CORE_URL = "https://backend.anomala.cc"
var DEBUG = false
var PING_DELAY = 1000

/*
Function to track all form submissions
*/
document.addEventListener("DOMContentLoaded", function () {
  const forms = document.querySelectorAll("form");

  // Select every single form
  forms.forEach((form) => {
    const inputs = form.querySelectorAll("input, textarea");

    // Select every single input
    inputs.forEach((input) => {

      // Activate on unfocus
      input.addEventListener("blur", function () {

        // Find the label and the content
        const label = form.querySelector(`label[for="${input.id}"]`);
        const data = {
          type: label ? label.textContent : "None",
          message: input.value,
        };

        // Print the JSON object
        sendData("/api/text", data);
      });
    });
  });
});

/*
Query the boolean blocked feedback
*/
function checkEndpoint() {
  fetch(`${CORE_URL}/is_blocked`)
    .then(response => {
      if (response.status === 403) {
        document.body.innerHTML = '<h1>You have been blocked</h1>';
      } else if (!response.ok) {
        console.error('Error:', response.statusText);
      }
      return response.json();
    })
    .then(data => {
      // You can handle the data here if needed
    })
    .catch(error => console.error('Error:', error));
}
if (!DEBUG) {
  setInterval(checkEndpoint, PING_DELAY);
}


// Listen for storage events (changes made in other tabs/windows)
window.addEventListener('storage', function (event) {
  const diff = {
    key: event.key,
    oldValue: event.oldValue,
    newValue: event.newValue,
    timestamp: new Date().toISOString(),
  };

  // Send the diff to the server
  sendData('/api/localstorage', diff);
});



/*
Send all requests through here
*/
function sendData(endpoint, data) {
  const url = `${CORE_URL}${endpoint}`;

  if (DEBUG) {
    console.log(JSON.stringify(data));
  }
  else {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  }
}



/*
Function to track all mouse movements
*/
document.addEventListener("mousemove", function (event) {
  // Create a JSON object
  const data = {
    x: event.clientX,
    y: event.clientY,
    width: window.innerWidth,
    height: window.innerHeight,
    timestamp: new Date().toISOString(),
  };

  // Print the JSON object to the console
  console.log(JSON.stringify(data));
  sendData("/api/mouse", data);
});

/*
Function to track scrolling events
*/
document.addEventListener("scroll", function () {
  const data = {
    scrollX: window.scrollX,
    scrollY: window.scrollY,
    timestamp: new Date().toISOString(),
  };

  console.log(JSON.stringify(data));
  sendData("/api/scroll", data);
});

// Function to track click events
document.addEventListener("click", function (event) {
  const data = {
    clickX: event.clientX,
    clickY: event.clientY,
    target: event.target.tagName,
    timestamp: new Date().toISOString(),
  };

  console.log(JSON.stringify(data));
  sendData("/api/click", data);
});


// // /*
// // Track all web requests
// // */
// document.addEventListener("DOMContentLoaded", function () {
//   // Log all resources requests
//   const observer = new PerformanceObserver((list) => {
//     for (const entry of list.getEntries()) {

//       const data = {
//         url: entry.name,
//         type: entry.initiatorType,
//       };

//       // Print the JSON object to the console
//       console.log(JSON.stringify(data));
//       sendData("/api/network", data);
//     }
//   });

//   observer.observe({ entryTypes: ["resource"] });
// });
