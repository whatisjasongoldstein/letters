const { JSDOM } = require("jsdom");
const Readability = require("readability");

var doc = new JSDOM("<body>Here's a bunch of text</body>", {
  // url: "https://www.example.com/the-page-i-got-the-source-from",
});

let reader = new Readability(doc.window.document);

let article = reader.parse();

console.log(article);
