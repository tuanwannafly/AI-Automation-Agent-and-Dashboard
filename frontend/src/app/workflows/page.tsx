"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Template {
  id: string;
  name: string;
  description: string;
}

export default function WorkflowsPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/workflows/templates")
      .then(res => {
        setTemplates(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleRun = async (templateId: string) => {
    try {
      const res = await api.get(`/api/workflows/templates/${templateId}`);
      const yamlContent = res.data.content;

      // Upload workflow
      const blob = new Blob([yamlContent], { type: "text/yaml" });
      const file = new File([blob], `${templateId}.yaml`, { type: "text/yaml" });
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await api.post("/api/workflows", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert(`Workflow uploaded! ID: ${uploadRes.data.workflow_id}`);
    } catch (error) {
      alert("Failed to run workflow");
    }
  };

  if (loading) {
    return <div className="min-h-screen p-8 bg-gray-950 text-gray-100">Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8 bg-gray-950 text-gray-100">
      <h1 className="text-3xl font-bold mb-8">Workflow Templates</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {templates.map(template => (
          <div key={template.id} className="bg-gray-900 rounded-lg p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-2">{template.name}</h2>
            <p className="text-gray-400 text-sm mb-4">{template.description}</p>
            <button
              onClick={() => handleRun(template.id)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
            >
              Run Workflow
            </button>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <p className="text-gray-500 text-center mt-12">No templates available</p>
      )}
    </div>
  );
}