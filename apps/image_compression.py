import os
import subprocess
import streamlit as st
from PIL import Image
import sys
from .algorithms import adaptive_huffman, lzw, lz77


def decodeJPG(filename):
    cpp_file = r"apps\algorithms\decoder.cpp"
    executable = "decoder"
    subprocess.run(["g++", cpp_file, "-o", executable])
    subprocess.run([r".\\" + executable, filename])


def encodeJPG(filename):
    cpp_file = r"apps\algorithms\encoder.cpp"
    executable = "encoder"
    subprocess.run(["g++", cpp_file, "-o", executable])
    subprocess.run([r".\\encoder ", filename])


def get_file_size(file_path):
    return os.path.getsize(file_path)


def compress_images(uploaded_files, compression_algorithm, searchWindow=6, previewWindow=6):
    compressed_files = []

    if uploaded_files is not None:
        for i, uploaded_file in enumerate(uploaded_files):
            file_name = uploaded_file.name
            with open(file_name, 'wb') as f:
                f.write(uploaded_file.read())

            image = Image.open(uploaded_file)
            image_path = f"temp_images/{uploaded_file.name}"
            image.save(image_path)
            original_file_size = uploaded_file.size

            if compression_algorithm == 'Adaptive Huffman':
                output_path = f"CompressedFiles/{uploaded_file.name.split('.')[0]}_AHCompressed"
                _, compressed_file_size = adaptive_huffman.compress(image_path, output_path)
                with open(output_path, 'rb') as f:
                    compressed_file = f.read()

            elif compression_algorithm == 'LZW':
                compressor = lzw.LZW_IMG(path=image_path)
                compressed_file = compressor.compress()
                compressed_file_size = sys.getsizeof(str(compressed_file))

            elif compression_algorithm == 'LZ77':
                compressor = lz77.LZ77(path=image_path, searchWindowSize=searchWindow, previewWindowSize=previewWindow)
                compressed_file = compressor.compress()
                compressed_file_size = sys.getsizeof(str(compressed_file))

            elif compression_algorithm == 'JPG':
                encodeJPG(file_name)
                compressed_filename = os.path.splitext(file_name)[0] + ".jpg"
                compressed_file_size = os.path.getsize(compressed_filename)
                with open(compressed_filename, 'rb') as f:
                    compressed_file = f.read()

            compression_ratio = original_file_size / compressed_file_size
            compression_percent = (1 - compressed_file_size / original_file_size) * 100

            compressed_files.append((compressed_file, original_file_size, compressed_file_size, compression_ratio,
                                     compression_percent))
    return compressed_files


def decompress_images(compressed_files, decompression_algorithm):
    decompressed_images = []

    for compressed_file in compressed_files:
        

        if decompression_algorithm == 'Adaptive Huffman':
            input_path = f"CompressedFiles/{compressed_file.name}"
            output_path = f"DecompressedFiles/{compressed_file.name.split('.')[0]}.bmp"
            adaptive_huffman.extract(input_path, output_path, (0, 255))
            decompressed_image = Image.open(output_path)

        elif decompression_algorithm == 'LZW':
            decompressor = lzw.LZW_IMG(file=compressed_file)
            decompressed_image = decompressor.decompress()
        elif decompression_algorithm == 'LZ77':
            decompressor = lz77.LZ77(file=compressed_file)
            decompressed_image = decompressor.decompress()
        elif decompression_algorithm == 'JPG':
            file_name = str(compressed_file.name)
            with open(file_name, "wb") as f:
                f.write(compressed_file.read())
            decodeJPG(file_name)
            decompressed_image = Image.open(os.path.splitext(file_name)[0] + ".bmp")

        decompressed_images.append(decompressed_image)

    return decompressed_images


def image_compression():
    st.title("Image Compression")

    mode_options = ['Compress', 'Decompress']
    mode = st.sidebar.radio("Select mode", mode_options)

    if mode == 'Compress':
        uploaded_files = st.file_uploader("Choose images", accept_multiple_files=True,
                                          type=['bmp'], key="image")

        compression_options = ['Adaptive Huffman', 'LZW', 'LZ77', 'JPG']
        compression_algorithm = st.selectbox("Select compression algorithm", compression_options)
        if compression_algorithm == 'LZ77':
            searchWindow = st.slider("Enter the search window size:", min_value=1, step=1)
            previewWindow = st.slider("Enter the preview window size:", min_value=1, step=1)

        if st.button("Compress"):
            if not uploaded_files:
                st.warning("Please upload at least one image.")
                return
            if compression_algorithm == 'LZ77':
                compressed_files = compress_images(uploaded_files, compression_algorithm, searchWindow, previewWindow)
            else:
                compressed_files = compress_images(uploaded_files, compression_algorithm)

            st.markdown("**Download compressed files:**")
            for i, compressed_file in enumerate(compressed_files):
                st.markdown(f"**Original File Size:** {compressed_file[1]} bytes")
                st.markdown(f"**Compressed File Size:** {compressed_file[2]} bytes")
                st.markdown(f"**Compression Ratio:** {compressed_file[3]:.2f}")
                st.markdown(f"**Compression Percent:** {compressed_file[4]:.2f}%")

                if compression_algorithm == "JPG":
                    st.download_button(
                        label="Download",
                        data=compressed_file[0],
                        file_name=os.path.splitext(uploaded_files[i].name)[0] + ".jpg"
                    )
                    st.markdown("---")
                elif compression_algorithm == "Adaptive Huffman":
                    st.download_button(
                        label="Download",
                        data=compressed_file[0],
                        file_name=uploaded_files[i].name.split('.')[0] + "_AHCompressed"
                    )
                    st.markdown("---")
                else:
                    st.download_button(
                        label="Download",
                        data=compressed_file[0],
                        file_name=uploaded_files[i].name.split('.')[0] + ".txt"
                    )
                    st.markdown("---")

    elif mode == 'Decompress':
        st.markdown("**Upload compressed files**")
        compressed_files = st.file_uploader("Choose files", accept_multiple_files=True,
                                            key="compressed_files")

        decompression_options = ['Adaptive Huffman', 'LZW', 'LZ77', 'JPG']
        decompression_algorithm = st.selectbox("Select decompression algorithm", decompression_options)

        if st.button("Decompress"):
            if not compressed_files:
                st.warning("Please upload at least one compressed file.")
                return

            decompressed_images = decompress_images(compressed_files, decompression_algorithm)

            st.markdown("----")
            st.success("Decompression completed!")
            st.markdown("**Original Images:**")
            for i, image in enumerate(decompressed_images):
                st.image(image)
                if decompression_algorithm == 'JPG':
                    filename = os.path.splitext(compressed_files[i].name)[0] + ".bmp"
                    with open(filename, 'rb') as f:
                        data = f.read()
                    st.download_button(
                        label="Download",
                        data=data,
                        file_name=filename
                    )
                    st.markdown("---")


def run():
    st.sidebar.title("Image Compression App")
    image_compression()
