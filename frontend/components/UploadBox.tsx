'use client';

import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, Image as ImageIcon, Loader2, Video } from 'lucide-react';

interface UploadBoxProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}

export default function UploadBox({ onUpload, isLoading }: UploadBoxProps) {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file) return;
    
    setSelectedFile(file);
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
      setPreview('video-file'); 
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };

  const handleRemove = () => {
    setPreview(null);
    setSelectedFile(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <AnimatePresence mode="wait">
        {preview ? (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative rounded-2xl overflow-hidden bg-zinc-900/50 border border-zinc-800"
          >
            <div className="aspect-video relative flex items-center justify-center bg-black/40">
              {preview === 'video-file' ? (
                <div className="flex flex-col items-center gap-4">
                  <Video className="w-16 h-16 text-white" />
                  <span className="text-zinc-400 font-medium">{selectedFile?.name}</span>
                </div>
              ) : (
                <img
                  src={preview!}
                  alt="Preview"
                  className="w-full h-full object-contain"
                />
              )}
              <button
                onClick={handleRemove}
                className="absolute top-4 right-4 p-2 rounded-full bg-black/50 backdrop-blur-sm text-white hover:bg-white hover:text-black transition-all duration-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-6 flex justify-center">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleUpload}
                disabled={isLoading}
                className="px-8 py-3 rounded-xl bg-white text-black font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:bg-zinc-200"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>{selectedFile?.type.startsWith('video/') ? 'Analyzing Video...' : 'Analyzing Image...'}</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    <span>Analyze Road</span>
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 ${
                dragActive
                  ? 'border-white bg-white/5'
                  : 'border-zinc-800 hover:border-zinc-700 bg-zinc-900/30'
              }`}
            >
              <input
                ref={inputRef}
                type="file"
                accept="image/*,video/*"
                onChange={handleChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="flex flex-col items-center justify-center py-16 px-6">
                <motion.div
                  animate={{
                    scale: dragActive ? 1.1 : 1,
                  }}
                  transition={{ type: 'spring', stiffness: 300 }}
                  className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4 border border-zinc-800"
                >
                  <ImageIcon className="w-8 h-8 text-white" />
                </motion.div>
                <h3 className="text-xl font-bold text-white mb-2">
                  Upload road media
                </h3>
                <p className="text-zinc-500 text-center max-w-md">
                  Drag and drop road images or videos here, or click to browse files.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}