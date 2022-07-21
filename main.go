/*
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <filip.katulski@cern.ch> wrote this file.  As long as you retain this notice
 * you can do whatever you want with this stuff. If we meet some day, and you
 * think this stuff is worth it, you can buy me a beer in return.
 * 																Filip Katulski
 * ----------------------------------------------------------------------------
 */

package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"

	"github.com/go-echarts/go-echarts/v2/charts"
	"github.com/go-echarts/go-echarts/v2/opts"
	"github.com/go-echarts/go-echarts/v2/types"
)

func randomData() []opts.LineData {

	data := make([]opts.LineData, 0)
	for i := 0; i < 7; i++ {
		data = append(data, opts.LineData{Value: rand.Intn(300), XAxisIndex: rand.Intn(300)})
	}
	return data
}

func randomScatterData() []opts.ScatterData {

	data := make([]opts.ScatterData, 0)

	for i := 0; i < 7; i++ {
		data = append(data, opts.ScatterData{Value: rand.Intn(300)})
	}
	return data
}

func httpserver(w http.ResponseWriter, _ *http.Request) {

	line := charts.NewLine()

	line.SetGlobalOptions(
		charts.WithInitializationOpts(opts.Initialization{Theme: types.ThemeInfographic}),
		charts.WithTitleOpts(opts.Title{
			Title:    "Line charts",
			Subtitle: "Rendered by the http server",
		}))

	line.SetXAxis([]int{0, 1, 300}).
		AddSeries("Category A", randomData())

	line.SetSeriesOptions(charts.WithLineChartOpts(opts.LineChart{Smooth: false}))
	line.Render(w)

	scatter := charts.NewScatter()
	scatter.SetGlobalOptions(
		charts.WithInitializationOpts(opts.Initialization{Theme: types.ThemeEssos}),
		charts.WithTitleOpts(opts.Title{
			Title:    "Test scatter",
			Subtitle: "Rendered test scatter",
		}))
	scatter.SetXAxis(10).
		AddSeries("Cat 1", randomScatterData())
	scatter.Render(w)

}

func main() {
	displayHeader()
	initFlags()

	data, err := parseDataFile(timelinefile)
	if err != nil {
		log.Fatalf("Could not read file %s: %v", timelinefile, err)
	}

	plotTypeSelection(plots, podstate, data)

	http.HandleFunc("/", httpserver)
	fmt.Println("Server started at port 8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}
