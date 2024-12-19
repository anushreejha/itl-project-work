import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { TextField, Button, Typography } from "@mui/material";
import axios from "axios";
import { API_URL } from "@/lib/const";

export default function CreatePost() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [author, setAuthor] = useState("");
  const router = useRouter();
  const { action, id } = router.query;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (action === "edit" && id) {
        await axios.put(`${API_URL}/blogs/${id}`, { title, content, author });
      } else {
        await axios.post(`${API_URL}/blogs`, { title, content, author });
      }
      router.push("/");
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (action === "edit" && id) {
      const fetchPost = async () => {
        try {
          const res = await axios.get(`${API_URL}/blogs/${id}`);
          setTitle(res.data.data.title);
          setContent(res.data.data.content);
          setAuthor(res.data.data.author);
        } catch (error) {
          console.error(error);
        }
      };
      fetchPost();
    }
  }, [action, id]); // Fixed dependency warning

  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom>
        {action === "edit" ? "Edit" : "Create"} Post
      </Typography>
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField
          label="Title"
          variant="outlined"
          fullWidth
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <TextField
          label="Author"
          variant="outlined"
          fullWidth
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          required
        />
        <TextField
          label="Content"
          variant="outlined"
          fullWidth
          multiline
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <Button type="submit" variant="contained" color="primary">
          {action === "edit" ? "Update" : "Create"} Post
        </Button>
      </form>
    </Layout>
  );
}
