package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"github.com/spf13/pflag"
)


var (
	ethel_add string
	username string
	password string
)

func init() {
	pflag.StringVar(&ethel_add, "address", "", "Address of Ethel")
	pflag.StringVar(&username, "username", "", "Username")
	pflag.StringVar(&password, "password", "", "Password")
	pflag.Parse()
}

func main() {
	fmt.Println(ethel_add)
	fmt.Println(username)
	fmt.Println(password)
	
	create_account(username, password)
	refresh_account(username, password)
	view_account(username, password)
}

func http_post(posturl string, data map[string]string) string {
	postdata, _ := json.Marshal(data)
	responseBody := bytes.NewBuffer(postdata)

	resp, err := http.Post(posturl, "application/json", responseBody)
	if err != nil {
		log.Fatalln(err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalln(err)
	}
	sb := string(body)
	return sb
}

func http_get(get_url string, getparam map[string]string) string {
	params := url.Values{}
	for key, value := range getparam {
		params.Add(key, value)
	}
	url := get_url + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		log.Fatalln(err)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalln(err)
	}
	sb := string(body)
	return sb
}

func create_account(name string, passwd string) {
	postdata := map[string]string{
		"username": name,
		"password": passwd,
	}
	resp := http_post(ethel_add+"/account/new", postdata)
	fmt.Println(resp)
}

func refresh_account(name string, passwd string) {
	postdata := map[string]string{
		"username": name,
		"password": passwd,
	}
	resp := http_post(ethel_add+"/account/refresh", postdata)
	fmt.Println(resp)
}

func view_account(name string, passwd string) {
	param := map[string]string{
		"username": name,
		"password": passwd,
	}
	resp := http_get(ethel_add+"/account/get?", param)
	fmt.Println(resp)
}
