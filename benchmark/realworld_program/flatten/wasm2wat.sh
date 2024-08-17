for file in `ls `
    do
    wat=".wat"
    if [[ $file =~ ".wasm" ]]
    then
        echo $file
        wasm2wat $file -o ${file%.wasm*}${wat}
    fi
#        rm ${file%.wasm*}${wat}
    done