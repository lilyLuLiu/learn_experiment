package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/gocolly/colly"
)

type Industry struct {
	Name, Value string
}

var industries []Industry

func main() {
	target_url := "https://account-manager-stage.app.eng.rdu2.redhat.com"
	fmt.Printf("We are going to expolore %v\n", target_url)

	// initialize the collector
	c := colly.NewCollector()
	c.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"

	css_selctor := "//*[@id='account_new']/div/label"
	c.OnXML(css_selctor, func(e *colly.XMLElement) {
		trimTitle := strings.TrimSpace(e.Text)
		dataset := Industry{
			Name:  trimTitle,
			Value: "null",
		}
		industries = append(industries, dataset)
	})

	// connect to the target site
	c.Visit(target_url)


	r := writeJsonFile(industries)
	if !r {
		log.Fatalln("Failed to write data to json file")
	}
	data := readJsonFile("userfile.json")
	if !r {
		log.Fatalln("Failed to read data from json file")
	}
	for _, title := range data {
		fmt.Println(title)
	}
}

func writeJsonFile(data []Industry) bool {
	jsonbyte, err := json.Marshal(data)
	if err != nil {
		log.Fatal(err)
		return false
	}
	err = os.WriteFile("userfile.json", jsonbyte, 0644)
	if err != nil {
		log.Fatal(err)
		return false
	}
	return true
}
func readJsonFile(filename string) []Industry {
	content, err := os.ReadFile(filename)
	if err != nil {
		log.Fatal(err)
		return nil
	}
	var filedata []Industry
	err = json.Unmarshal(content, &filedata)
	if err != nil {
		log.Fatal(err)
		return nil
	}
	return filedata
}
