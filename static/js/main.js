document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const symptomsInput = document.getElementById('symptomsInput');
    const symptomsListContainer = document.getElementById('symptomsListContainer');
    const symptomsList = document.getElementById('symptomsList');
    const availableSymptoms = document.getElementById('availableSymptoms');
    
    // Only run symptoms-related code if we're on the correct page (home/index page)
    if (symptomsInput && availableSymptoms) {
        // Fetch available symptoms from the server
        fetch('/symptoms')
            .then(response => response.json())
            .then(data => {
                const symptoms = data.symptoms;
                
                // Populate the available symptoms sidebar
                symptoms.forEach(symptom => {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-secondary me-1 mb-1 symptom-tag';
                    badge.textContent = symptom;
                    badge.addEventListener('click', function() {
                        addSymptomToInput(symptom);
                    });
                    availableSymptoms.appendChild(badge);
                });
                
                // Also add common symptoms to the dropdown if available
                if (symptomsList) {
                    const commonSymptoms = [
                        'fever', 'cough', 'headache', 'fatigue', 'dizziness', 
                        'nausea', 'vomiting', 'chest_pain', 'back_pain', 'joint_pain',
                        'abdominal_pain', 'muscle_pain', 'sore_throat', 'runny_nose', 'shortness_of_breath',
                        'rash', 'chills', 'diarrhea', 'constipation', 'loss_of_appetite'
                    ];
                    
                    commonSymptoms.forEach(symptom => {
                        if (symptoms.includes(symptom)) {
                            const badge = document.createElement('span');
                            badge.className = 'badge bg-primary me-1 mb-1 symptom-tag';
                            badge.textContent = symptom;
                            badge.addEventListener('click', function() {
                                addSymptomToInput(symptom);
                            });
                            symptomsList.appendChild(badge);
                        }
                    });
                }
            })
            .catch(error => console.error('Error fetching symptoms:', error));
        
        // Show dropdown when input is focused
        symptomsInput.addEventListener('focus', function() {
            if (symptomsListContainer) {
                symptomsListContainer.classList.remove('d-none');
            }
        });
        
        // Hide dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (symptomsListContainer && symptomsInput && 
                !symptomsInput.contains(event.target) && 
                !symptomsListContainer.contains(event.target)) {
                symptomsListContainer.classList.add('d-none');
            }
        });
        
        // Filter symptoms based on input
        symptomsInput.addEventListener('input', function() {
            if (symptomsListContainer && symptomsList) {
                const inputValue = this.value.toLowerCase();
                const lastSymptom = inputValue.split(',').pop().trim();
                
                // Show/hide dropdown based on whether there's input
                if (lastSymptom.length > 0) {
                    symptomsListContainer.classList.remove('d-none');
                    
                    // Filter symptoms in the dropdown based on input
                    const badges = symptomsList.querySelectorAll('.symptom-tag');
                    badges.forEach(badge => {
                        const symptomText = badge.textContent.toLowerCase();
                        if (symptomText.includes(lastSymptom)) {
                            badge.style.display = 'inline-block';
                        } else {
                            badge.style.display = 'none';
                        }
                    });
                } else {
                    // Show all options if no specific filter
                    const badges = symptomsList.querySelectorAll('.symptom-tag');
                    badges.forEach(badge => {
                        badge.style.display = 'inline-block';
                    });
                }
            }
        });
    }
    
    // Function to add symptom to input field (globally accessible)
    window.addSymptomToInput = function(symptom) {
        if (symptomsInput) {
            let currentValue = symptomsInput.value;
            let symptoms = currentValue.split(',').map(s => s.trim()).filter(s => s);
            
            // Check if the symptom is already added
            if (!symptoms.includes(symptom)) {
                if (symptoms.length > 0) {
                    symptomsInput.value = symptoms.join(', ') + ', ' + symptom;
                } else {
                    symptomsInput.value = symptom;
                }
            }
            
            // Focus back on the input
            symptomsInput.focus();
        }
    };
    
    // Scroll to diagnosis results if they exist
    const diagnosisResults = document.getElementById('diagnosisResults');
    if (diagnosisResults) {
        setTimeout(() => {
            // Calculate proper scroll position to keep form input in view too
            const formTop = document.getElementById('symptomForm')?.offsetTop || 0;
            // Scroll to position that shows both the form and results
            window.scrollTo({
                top: formTop - 20, // Smaller offset to keep input visible
                behavior: 'smooth'
            });
            
            // Highlight the results area briefly
            diagnosisResults.classList.add('highlight-results');
            setTimeout(() => {
                diagnosisResults.classList.remove('highlight-results');
            }, 1000);
        }, 200); // Faster delay for more immediate feedback
    }
    
    // Blog page subscription form handling
    const subscriptionForm = document.getElementById('subscriptionForm');
    if (subscriptionForm) {
        subscriptionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('subscriptionEmail').value;
            
            fetch('/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email }),
            })
            .then(response => response.json())
            .then(data => {
                const alertElement = document.createElement('div');
                alertElement.className = data.success 
                    ? 'alert alert-success alert-dismissible fade show mt-3' 
                    : 'alert alert-danger alert-dismissible fade show mt-3';
                alertElement.innerHTML = `
                    ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                subscriptionForm.appendChild(alertElement);
                
                if (data.success) {
                    document.getElementById('subscriptionEmail').value = '';
                }
                
                // Auto remove the alert after 5 seconds
                setTimeout(() => {
                    alertElement.remove();
                }, 5000);
            })
            .catch(error => console.error('Error:', error));
        });
    }
});