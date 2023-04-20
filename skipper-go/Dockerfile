FROM ghcr.io/oshied/base-go1.20:bionic AS BUILD
WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY . ./

RUN make build

FROM gcr.io/distroless/base-debian11:debug

WORKDIR /usr/local/bin

COPY --from=BUILD /app/backrunner /usr/local/bin/backrunner

# you must add to ENTRYPOINT "--config=</path/to/skipper-go/config>", "--multihop=<YOUR CONTRACT ADDRESS HERE>", "--key=<YOUR PRIVATE KEY HERE>"
ENTRYPOINT ["/usr/local/bin/backrunner", "start"]
