import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DetectionResult {
  bbox: number[];
  area: number;
  severity: 'small' | 'medium' | 'large';
  workers: number;
  cost: number;
  time: number;
  confidence: number;
}

export interface DetectionResponse {
  detections: DetectionResult[];
  total_potholes: number;
  total_cost: number;
  severity_distribution: {
    small: number;
    medium: number;
    large: number;
  };
  image_url?: string;
  report_url?: string;
  original_url?: string;
}

export interface VideoDetectionResponse {
  detections: DetectionResult[];
  total_potholes: number;
  total_cost: number;
  severity_distribution: {
    small: number;
    medium: number;
    large: number;
  };
  report_url: string;
  video_url: string;
  original_url?: string;
}

export const detectPotholes = async (file: File): Promise<DetectionResponse> => {
  console.log("detectPotholes triggered with file:", file.name);
  const formData = new FormData();
  formData.append('file', file);

  console.log("Preparing request to detect potholes...");
  console.log("API URL:", `${API_BASE_URL}/detect`);

  try {
    console.log("Sending request to backend...");
    const response = await axios.post<DetectionResponse>(
      `${API_BASE_URL}/detect`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    console.log("Response received from backend:", response);
    console.log("Response data:", response.data);
    return response.data;
  } catch (error) {
    console.error("API call detectPotholes failed:", error);
    throw error;
  }
};
export const detectVideo = async (file: File): Promise<VideoDetectionResponse> => {
  console.log("detectVideo triggered with file:", file.name);
  const formData = new FormData();
  formData.append('file', file);

  console.log("Preparing request to detect video...");
  console.log("API URL:", `${API_BASE_URL}/detect/video`);

  try {
    console.log("Sending request to backend...");
    const response = await axios.post<VideoDetectionResponse>(
      `${API_BASE_URL}/detect/video`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 900000, 
      }
    );

    console.log("Response received from backend:", response);
    console.log("Response data:", response.data);
    return response.data;
  } catch (error) {
    console.error("API call detectVideo failed:", error);
    throw error;
  }
};

/** @deprecated Use persistent original_url from backend response instead */
export const createImageUrl = (file: File): string => {
  return URL.createObjectURL(file);
};

export const getFullReportUrl = (reportPath: string): string => {
  if (!reportPath) return '';
  if (reportPath.startsWith('http')) return reportPath;
  const fullUrl = `${API_BASE_URL}${reportPath}`;
  console.log(`DEBUG: Resolving full report URL for ${reportPath} -> ${fullUrl}`);
  return fullUrl;
};