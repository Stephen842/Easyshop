/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
     './shop/templates/pages/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        'magnolia': ['Magnolia Script', 'cursive'],
      },
    },
  },
  plugins: [],
}

