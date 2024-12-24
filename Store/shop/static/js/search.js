document.getElementById("search-icon").addEventListener("click", function(e) {
    e.preventDefault();  // Prevent the default behavior of the link
    
    const searchContainer = document.getElementById("search-container");
    const input = document.getElementById("search-input");
  
    // Toggle visibility of the search container
    searchContainer.classList.toggle("hidden");
  
    // Toggle the input field's size and visibility
    if (searchContainer.classList.contains("hidden")) {
      // If it's hidden, collapse the input field
      input.classList.add("w-0", "opacity-0", "p-0", "border-transparent");
      input.classList.remove("w-60", "opacity-100", "p-2", "border-gray-300");
    } else {
      // If it's visible, expand the input field
      input.classList.remove("w-0", "opacity-0", "p-0", "border-transparent");
      input.classList.add("w-60", "opacity-100", "p-2", "border-gray-300");
    }
  });
  