document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('patientSearchInput');
            const patientListContainer = document.getElementById('patientListContainer');
            const patientCards = patientListContainer.querySelectorAll('.patient-card-wrapper'); // Select the wrappers
            const noResultsMessage = document.getElementById('noResultsMessage');

            if (!searchInput || !patientListContainer || !noResultsMessage) {
                console.error("Search elements not found!");
                return; // Stop if essential elements are missing
            }

            searchInput.addEventListener('keyup', function() {
                const searchTerm = searchInput.value.toLowerCase().trim();
                let visibleCount = 0;

                patientCards.forEach(cardWrapper => {
                    // Find the actual card inside the wrapper to get text content
                    const card = cardWrapper.querySelector('.patient-card');
                    if (!card) return; // Skip if card not found within wrapper

                    // Combine relevant text content from the card
                    const patientName = card.querySelector('.patient-name')?.textContent || '';
                    const searchableElements = card.querySelectorAll('.searchable-text'); // Get specifically marked text
                    let cardText = patientName;

                    searchableElements.forEach(el => {
                        cardText += ' ' + (el.textContent || '');
                    });

                    const cardTextLower = cardText.toLowerCase();

                    // Check if card text includes the search term
                    if (cardTextLower.includes(searchTerm)) {
                        cardWrapper.style.display = ''; // Show the wrapper (column)
                        visibleCount++;
                    } else {
                        cardWrapper.style.display = 'none'; // Hide the wrapper (column)
                    }
                });

                // Show or hide the 'No Results' message
                if (visibleCount === 0 && patientCards.length > 0) { // Only show if there were cards to search
                    noResultsMessage.style.display = 'block';
                } else {
                    noResultsMessage.style.display = 'none';
                }
            });
        });