## How to use
First terminal
> go run credit_card.go 8080

Second terminal
> curl -X POST http://localhost:8080/ -d '{ "number": "4003600000000014" }' 

received result: {"valid":true}

## What learned
### Create a http server
> http.HandleFunc("/", creditCardValidator)

- First parameter "/" is the location of url
    - If this parmater is /test, then the request address is http://localhost:8080/test 
- Second parameter is a function that deal the http request.

> http.ListenAndServe(":"+port, nil)

Set the listen address and start the http server

### Http handle function
> func funcNmae(writer http.ResponseWriter, request *http.Request)

- Get the request body
   > json.NewDecoder(request.Body).Decode((&cardNumber))

- Check the request type
    > if request.Method != http.MethodPost {}

- Write response 
    - Response with error
    > http.Error(writer, "Invalid request method", http.StatusMethodNotAllowed)

    - Reponse with json data
    > writer.Header().Set("Content-Type", "application/json")
	writer.Write(jsonResponse)
