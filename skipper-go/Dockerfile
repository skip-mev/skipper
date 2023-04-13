FROM golang:1.20-alpine
WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY . ./
RUN go build -o backrunner
# you must add to ENTRYPOINT "--config=</path/to/skipper-go/config>", "--multihop=<YOUR CONTRACT ADDRESS HERE>", "--key=<YOUR PRIVATE KEY HERE>"
ENTRYPOINT ["/app/backrunner", "start"]