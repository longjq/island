CMD=`../protoc/bin/protoc --python_out=../code/proto *.proto`

CMD=`../protoc/bin/protoc -oisland.desc *.proto`

CMD=`cp island.desc ../client/res/raw`

CMD=`../protoc/bin/protoc --java_out=../client/src *.proto`
