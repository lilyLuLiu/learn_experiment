package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

func luhnAlgorithm(cardNumber string) bool {
    // this function implements the luhn algorithm
    // it takes as argument a cardnumber of type string
    // and it returns a boolean (true or false) if the
    // card number is valid or not

    // initialise a variable to keep track of the total sum of digits
    total := 0
    // Initialize a flag to track whether the current digit is the second digit from the right.
    isSecondDigit := false

    // iterate through the card number digits in reverse order
    for i := len(cardNumber) - 1; i >= 0; i-- {
        // conver the digit character to an integer
        digit := int(cardNumber[i] - '0')

        if isSecondDigit {
            // double the digit for each second digit from the right
            digit *= 2
            if digit > 9 {
                // If doubling the digit results in a two-digit number,
                //subtract 9 to get the sum of digits.
                digit -= 9
            }
        }

        // Add the current digit to the total sum
        total += digit

        //Toggle the flag for the next iteration.
        isSecondDigit = !isSecondDigit
    }

    // return whether the total sum is divisible by 10
    // making it a valid luhn number
    return total%10 == 0
}

type Response struct {
	Valid bool `json:"valid"`
} 

//test of comment
func creditCardValidator(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		http.Error(writer, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}
	var cardNumber struct {
        Number string `json:"number"` // Number field holds the credit card number.
    }

	err := json.NewDecoder(request.Body).Decode((&cardNumber))
	if err != nil {
		http.Error(writer, "Invalid Json payload", http.StatusBadRequest)
		return
	}

	isvalid := luhnAlgorithm(cardNumber.Number)
	response := Response{Valid: isvalid}

	jsonResponse, err := json.Marshal(response)
	if err != nil {
		http.Error(writer, "Error creating response", http.StatusInternalServerError)
		return
	}

	writer.Header().Set("Content-Type", "application/json")
	writer.Write(jsonResponse)
}

func main() {
	args := os.Args
	port := args[1]

	http.HandleFunc("/", creditCardValidator)
	fmt.Println("Listening on port:", port)

	err:= http.ListenAndServe(":"+port, nil)
	if err != nil {
		fmt.Println("Error:", err)
	}
}
