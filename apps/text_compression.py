from decimal import getcontext

import sys
import pandas as pd
import streamlit as st
from apps.algorithms import ae, huffman, lzw, lz77


def get_file_size(file_path):
    with open(file_path, 'rb') as file:
        return len(file.read())


def text_compression():
    st.title("Text Compression")
    mode = st.sidebar.radio('Select App', ["Compress", "Decompress"])

    options = ['Enter', 'Upload']
    selection = st.sidebar.selectbox("Select option ", options)
    output_text = st.empty()
    check_point = 0
    compression_options = ['Huffman', 'Arithmetic', 'LZ77', 'LZW']
    compression_algorithm = st.sidebar.selectbox("Select compression algorithm", compression_options)

    def compress(input_text, name_path=None):
        encoding, encoding_text = None, ""
        decoded_output = None
        frequency_table = {}
        before, after = None, None

        if mode == "Compress":
            if not input_text:
                st.warning("Please enter some text.")
                return

            if compression_algorithm == 'Huffman':
                if st.button("Compress"):
                    HF = huffman.Huffman(input_text)
                    encoding, tree, codes, before, after = HF.encode_text()

                    st.subheader("Encoding Table:")
                    table_data = []
                    for symbol, code in codes.items():
                        table_data.append([symbol, code])
                    table = pd.DataFrame(
                        table_data,
                        columns=("Symbol", "Code"))
                    st.table(table)


            elif compression_algorithm == 'Arithmetic':
                precision = st.number_input("Enter the precision:", min_value=1, value=28, step=1)

                getcontext().prec = precision
                if st.button("Compress"):
                    for char in input_text:
                        if char in frequency_table:
                            frequency_table[char] += 1
                        else:
                            frequency_table[char] = 1

                    AE = ae.ArithmeticEncoding(frequency_table=frequency_table)

                    st.text(f"Original Message: {input_text}")
                    encoded_msg, encoder, interval_min_value, interval_max_value = AE.encode(msg=input_text,
                                                                                             probability_table=AE.probability_table)
                    st.text(f"Encoded Message: {encoded_msg}")
                    binary_code, encoder_binary = AE.encode_binary(float_interval_min=interval_min_value,
                                                                   float_interval_max=interval_max_value)
                    st.text(f"The binary code is: {binary_code}")

            elif compression_algorithm == 'LZW':
                if st.button("Compress"):
                    compressor = lzw.LZW_TEXT()
                    encoding = compressor.compress_text(input_text)
                    before, after = len(input_text) * 8, len(encoding) * 8

            elif compression_algorithm == 'LZ77':
                searchWindow = st.slider("Enter the search window size:", min_value=1, step=1)
                previewWindow = st.slider("Enter the preview window size:", min_value=1, step=1)
                if (st.button("Compress")):
                    compressor = lz77.LZ77(searchWindowSize=searchWindow, previewWindowSize=previewWindow)
                    encoding = compressor.encode_lz77(input_text)
                    before, after = len(input_text) * 8, len(encoding) * 8

            if after != None :
                percent_saved = (1 - after / before) * 100
                st.markdown("### Compression Results")
                st.text(f"Original Size: {before} bits")
                st.text(f"Compressed Size: {after} bits")
                st.text(f"Percent Saved: {percent_saved:.2f}%")

            if selection == 'Enter':
                st.text(f"Encoded output: {encoding}")

            elif selection == 'Upload':
                name_file_comp = uploaded_file.name.split('.')[0] + "_" + compression_algorithm + "Encode." + \
                                 uploaded_file.name.split('.')[1]

                if encoding != None:
                    st.download_button(
                            label="Download",
                            data=encoding,
                            file_name=name_file_comp
                        )
                st.markdown("---")

        if mode == "Decompress":
            if compression_algorithm == 'Huffman':
                if st.button("Decompress"):
                    HF = huffman.Huffman(input_text)
                    encoding, tree, codes, before, after = HF.encode_text()
                    decoded_output = HF.decoding_text(encoding, tree)
                    st.text(f"Encoded output: {encoding}")
                    output_text.text(f"Decoded output: {decoded_output}")

            elif compression_algorithm == 'Arithmetic':
                if st.button("Decompress"):
                    msg_length = len(input_text)
                    for char in input_text:
                        if char in frequency_table:
                            frequency_table[char] += 1
                        else:
                            frequency_table[char] = 1

                    AE = ae.ArithmeticEncoding(frequency_table=frequency_table)

                    encoded_msg, encoder, interval_min_value, interval_max_value = AE.encode(msg=input_text,
                                                                                             probability_table=AE.probability_table)

                    decoded_output, decoder = AE.decode(encoded_msg, msg_length, AE.probability_table)
                    decoded_output = "".join(decoded_output)
                    st.text(f"Encoded Message: {encoded_msg}")
                    st.text(f"Message Decoded Successfully? {input_text == decoded_output}")


            elif compression_algorithm == 'LZW':
                if st.button("Decompress"):
                    compressor = lzw.LZW_TEXT()
                    decoded_output = compressor.decompress_text(input_text)

            elif compression_algorithm == 'LZ77':
                if st.button("Decompress"):
                    compressor = lz77.LZ77()
                    decoded_output = compressor.decode_lz77(input_text)

            if selection == 'Enter':
                st.text(f"Decoded output: {decoded_output}")

            elif selection == 'Upload':
                name_file_comp = uploaded_file.name.split('.')[0] + "_" + compression_algorithm + "Decode." + \
                                 uploaded_file.name.split('.')[1]

                if decoded_output != None:
                    st.download_button(
                            label="Download",
                            data=decoded_output,
                            file_name=name_file_comp
                    )
                
        if decoded_output != None:
            st.text("Done!!!")

    if selection == 'Enter':
        input_text = st.text_area("Enter the text to compress:")
        compress(input_text)
    elif selection == 'Upload':
        uploaded_files = st.file_uploader("Choose text", accept_multiple_files=True, type=['txt'],
                                          key="text")

        for uploaded_file in uploaded_files:
            text_path = f"temp_texts/{uploaded_file.name}"
            input_text = uploaded_file.read()
            with open(text_path, 'w', encoding="utf-8") as file:
                file.write(input_text.decode())
            input_text = input_text.decode()
            compress(input_text, uploaded_file.name)

    if check_point == 1:
        return


def run():
    st.sidebar.title("Text Compression App")
    text_compression()