// Copyright ©2020 The go-fonts Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

// Copyright 2016 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

//go:build ignore
// +build ignore

package main

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"flag"
	"fmt"
	"go/format"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strings"
)

func main() {
	log.SetPrefix("liberation-gen: ")
	log.SetFlags(0)

	var (
		src = flag.String(
			"src",
			"https://github.com/liberationfonts/liberation-fonts/files/6418984/liberation-fonts-ttf-2.1.4.tar.gz",
			"remote tar-gz file holding TTF files for Liberation fonts",
		)
	)

	flag.Parse()

	tmp, err := ioutil.TempDir("", "go-fonts-liberation-")
	if err != nil {
		log.Fatalf("could not create tmp dir: %+v", err)
	}

	var (
		fname string
	)

	switch {
	case strings.HasPrefix(*src, "http://"),
		strings.HasPrefix(*src, "https://"):
		fname, err = fetch(tmp, *src)
		if err != nil {
			log.Fatalf("could not fetch Liberation sources: %+v", err)
		}
	default:
		fname = *src
	}

	f, err := os.Open(fname)
	if err != nil {
		log.Fatalf("could not open tar file: %+v", err)
	}
	defer f.Close()
	gr, err := gzip.NewReader(f)
	if err != nil {
		log.Fatalf("could not open gzip file: %+v", err)
	}
	defer gr.Close()

	log.Printf("inspecting tar file...")
	tr := tar.NewReader(gr)
	for {
		hdr, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatalf("could not read tar archive: %+v", err)
		}
		if !strings.HasSuffix(hdr.Name, suffix) {
			continue
		}
		err = gen(path.Base(hdr.Name), tr)
		if err != nil {
			log.Fatalf("could not generate font: %+v", err)
		}
	}
}

func fetch(tmp, src string) (string, error) {
	resp, err := http.Get(src)
	if err != nil {
		return "", fmt.Errorf("could not GET %q: %w", src, err)
	}
	defer resp.Body.Close()

	f, err := os.Create(path.Join(tmp, "liberation.tar.gz"))
	if err != nil {
		return "", fmt.Errorf("could not create zip file: %w", err)
	}
	defer f.Close()

	_, err = io.Copy(f, resp.Body)
	if err != nil {
		return "", fmt.Errorf("could not copy zip file: %w", err)
	}

	err = f.Close()
	if err != nil {
		return "", fmt.Errorf("could not save zip file: %w", err)
	}

	return f.Name(), nil
}

func gen(fname string, tr *tar.Reader) error {
	log.Printf("generating fonts package for %q...", fname)

	raw := new(bytes.Buffer)
	_, err := io.Copy(raw, tr)
	if err != nil {
		return fmt.Errorf("could not download TTF file: %w", err)
	}

	err = do(fname, raw.Bytes())
	if err != nil {
		return fmt.Errorf("could not generate package for %q: %w", fname, err)
	}

	return nil
}

func do(ttfName string, src []byte) error {
	fontName := fontName(ttfName)
	pkgName := pkgName(ttfName)
	if err := os.Mkdir(pkgName, 0777); err != nil && !os.IsExist(err) {
		return fmt.Errorf("could not create package dir %q: %w", pkgName, err)
	}

	b := new(bytes.Buffer)
	fmt.Fprintf(b, "// generated by go run gen-fonts.go; DO NOT EDIT\n\n")
	fmt.Fprintf(b, "// Package %s provides the %q TrueType font\n", pkgName, fontName)
	fmt.Fprintf(b, "// from the Liberation font family.\n")
	fmt.Fprintf(b, "package %[1]s // import \"github.com/go-fonts/liberation/%[1]s\"\n\n", pkgName)
	fmt.Fprintf(b, "// TTF is the data for the %q TrueType font.\n", fontName)
	fmt.Fprintf(b, "var TTF = []byte{")
	for i, x := range src {
		if i&15 == 0 {
			b.WriteByte('\n')
		}
		fmt.Fprintf(b, "%#02x,", x)
	}
	fmt.Fprintf(b, "\n}\n")

	dst, err := format.Source(b.Bytes())
	if err != nil {
		return fmt.Errorf("could not format source: %w", err)
	}

	err = ioutil.WriteFile(filepath.Join(pkgName, "data.go"), dst, 0666)
	if err != nil {
		return fmt.Errorf("could not write package source file: %w", err)
	}

	return nil
}

const suffix = ".ttf"

// fontName maps "Go-Regular.ttf" to "Go Regular".
func fontName(ttfName string) string {
	s := ttfName[:len(ttfName)-len(suffix)]
	s = strings.Replace(s, "-", " ", -1)
	return s
}

// pkgName maps "Go-Regular.ttf" to "goregular".
func pkgName(ttfName string) string {
	s := ttfName[:len(ttfName)-len(suffix)]
	s = strings.Replace(s, "-", "", -1)
	s = strings.ToLower(s)
	return s
}
