# cd manticore_nameOB
# pwd
# for file in `ls `
#     do
#     wat=".wat"
#     if [[ $file =~ ".wasm" ]]
#     then
#         echo $file
#         wasm2wat $file -o ${file%.wasm*}${wat}
#     fi
# #        rm ${file%.wasm*}${wat}
#     done
# cd ..

# cd manticore_memoryOB
# pwd
# for file in `ls `
#     do
#     wat=".wat"
#     if [[ $file =~ ".wasm" ]]
#     then
#         echo $file
#         wasm2wat $file -o ${file%.wasm*}${wat}
#     fi
# #        rm ${file%.wasm*}${wat}
#     done
# cd ..


# cd btree_nameOB
# pwd
# for file in `ls `
#     do
#     wat=".wat"
#     if [[ $file =~ ".wasm" ]]
#     then
#         echo $file
#         wasm2wat $file -o ${file%.wasm*}${wat}
#     fi
# #        rm ${file%.wasm*}${wat}
#     done
# cd ..

# cd btree_memoryOB
# pwd
# for file in `ls `
#     do
#     wat=".wat"
#     if [[ $file =~ ".wasm" ]]
#     then
#         echo $file
#         wasm2wat $file -o ${file%.wasm*}${wat}
#     fi
# #        rm ${file%.wasm*}${wat}
#     done
# cd ..


cd manticore_origin
pwd
for dir_file in `ls `
do

    echo $dir_file
    if [ -d "$dir_file" ]; then
      cd $dir_file
      for file in `ls `
          do
          wat=".wat"
          if [[ $file =~ ".wasm" ]]
          then
              wasm2wat $file -o ${file%.wasm*}${wat}
          fi
  #        rm ${file%.wasm*}${wat}
          done
      cd ..
    fi
done
cd ..


cd manticore_calltocallindirect
pwd
for dir_file in `ls `
do

    echo $dir_file
    if [ -d "$dir_file" ]; then
      cd $dir_file
      for file in `ls `
          do
          wat=".wat"
          if [[ $file =~ ".wasm" ]]
          then
              wasm2wat $file -o ${file%.wasm*}${wat}
          fi
  #        rm ${file%.wasm*}${wat}
          done
      cd ..
    fi
done
cd ..


cd manticore_flatten
pwd
for dir_file in `ls `
do

   echo $dir_file
   if [ -d "$dir_file" ]; then
     cd $dir_file
     for file in `ls `
         do
         wat=".wat"
         if [[ $file =~ ".wasm" ]]
         then
             wasm2wat $file -o ${file%.wasm*}${wat}
         fi
 #        rm ${file%.wasm*}${wat}
         done
     cd ..
   fi
done
cd ..