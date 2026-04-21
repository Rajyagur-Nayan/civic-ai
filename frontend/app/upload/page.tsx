"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import UploadBox from "@/components/UploadBox";
import { detectPotholes, detectVideo } from "@/services/api";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    console.log("handleUpload triggered");
    if (!file) {
      console.log("No file selected for upload");
      return;
    }
    console.log("Selected file:", file.name, "Type:", file.type, "Size:", file.size);

    setIsLoading(true);
    setError(null);

    try {
      console.log("Preparing to analyze asset...");
      let response: any;
      if (file.type.startsWith("video/")) {
        console.log("File detected as VIDEO");
        response = await detectVideo(file);
      } else {
        console.log("File detected as IMAGE");
        response = await detectPotholes(file);
      }

      console.log("Analysis successful. Backend response:", response);

      const resultData = {
        ...response,
        imageUrl: response.original_url || null,
        originalVideoUrl: response.original_url || null,
      };

      console.log("Saving resultData to sessionStorage:", resultData);
      sessionStorage.setItem("detectionResult", JSON.stringify(resultData));
      
      console.log("Navigating to /results...");
      router.push("/results");
    } catch (err: any) {
      console.error("handleUpload catch block triggered with error:", err);
      if (err.code === "ECONNABORTED" || err.message?.includes("timeout")) {
        setError(
          "Analysis timed out. Please try with a shorter video or a high-quality image.",
        );
      } else {
        setError("Failed to analyze the file. Please try again.");
      }
      console.error("Error details:", err);
    } finally {
      setIsLoading(false);
      console.log("handleUpload flow finished (finally block)");
    }
  };

  return (
    <div className="min-h-screen bg-black relative flex flex-col pt-32 px-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto w-full"
      >
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-white mb-4 uppercase">
            Start Analysis
          </h1>
          <p className="text-zinc-500 text-lg font-medium max-w-xl mx-auto">
            Upload road assets to generate high-precision repair intelligence
            and cost models.
          </p>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-8 p-4 rounded-2xl bg-white text-black font-bold text-center text-sm uppercase tracking-widest"
          >
            {error}
          </motion.div>
        )}

        <UploadBox onUpload={handleUpload} isLoading={isLoading} />
      </motion.div>

      {/* Background decoration - very subtle */}
      <div className="fixed bottom-0 left-0 w-full h-[30vh] bg-gradient-to-t from-zinc-900/20 to-transparent pointer-events-none" />
    </div>
  );
}
