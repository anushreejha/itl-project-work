import React, { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import { BlogPost } from "@/interfaces/BlogPost";
import {
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import Link from "next/link";
import { API_URL } from "@/lib/const";
import axios from "axios";
import { useRouter } from "next/router";

export default function Home() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const router = useRouter();

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${API_URL}/blogs/${id}`);
      setPosts(posts.filter((post) => post.id !== id));
    } catch (error) {
      console.error(error);
    }
    router.push("/");
  };

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const res = await axios.get(`${API_URL}/blogs`);
        setPosts(res.data.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchPosts();
  }, []);

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex justify-end">
          <Link href="/create" passHref>
            <Button variant="contained" color="primary">
              Create New Post
            </Button>
          </Link>
        </div>

        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="blog posts table">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Author</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {posts && posts.length > 0 ? (
                posts.map((post) => (
                  <TableRow key={post.id}>
                    <TableCell>
                      {new Date(post.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{post.title}</TableCell>
                    <TableCell>{post.author}</TableCell>
                    <TableCell>
                      <Link href={`/create?action=edit&id=${post.id}`} passHref>
                        <Button>Edit</Button>
                      </Link>
                      <Button onClick={() => handleDelete(post.id)}>Delete</Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    No posts available.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    </Layout>
  );
}
