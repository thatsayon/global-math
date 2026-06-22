"use client";

import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Trash2, Search, MessageSquare, FileText, Image as ImageIcon } from "lucide-react";
import { toast } from "sonner";
import {
  useGetAdminPostsQuery,
  useDeleteAdminPostMutation,
  useGetAdminCommentsQuery,
  useDeleteAdminCommentMutation,
} from "@/store/slices/api/moderationApiSlice";
import { AdminPost, AdminComment } from "@/types/moderation.type";
import { format } from "date-fns";

const formatDate = (d: string) => format(new Date(d), "MMM d, yyyy");

const getInitials = (first?: string | null, last?: string | null) =>
  `${first?.[0] || ""}${last?.[0] || ""}`.toUpperCase() || "?";

// ─── Delete Confirmation Dialog ─────────────────────────────────
const DeleteDialog = ({
  open,
  label,
  deleting,
  onConfirm,
  onClose,
}: {
  open: boolean;
  label: string;
  deleting: boolean;
  onConfirm: () => void;
  onClose: () => void;
}) => (
  <Dialog open={open} onOpenChange={onClose}>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Delete {label}</DialogTitle>
      </DialogHeader>
      <p className="text-gray-600 py-2">
        Are you sure you want to permanently delete this {label.toLowerCase()}? This action cannot be undone.
      </p>
      <DialogFooter>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="destructive" onClick={onConfirm} disabled={deleting}>
          {deleting ? "Deleting..." : `Delete ${label}`}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
);

// ─── Posts Tab ────────────────────────────────────────────────────
const PostsTab = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const { data, isLoading, isFetching } = useGetAdminPostsQuery({ page, search });
  const [deletePost, { isLoading: deleting }] = useDeleteAdminPostMutation();

  const posts = data?.results || [];
  const totalPages = Math.ceil((data?.count || 0) / 10);

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(1);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deletePost(deleteTarget).unwrap();
      toast.success("Post deleted successfully");
      setDeleteTarget(null);
    } catch {
      toast.error("Failed to delete post");
    }
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search by author or content..."
            className="pl-9"
          />
        </div>
        <Button onClick={handleSearch} variant="outline">Search</Button>
        {search && (
          <Button onClick={() => { setSearch(""); setSearchInput(""); setPage(1); }} variant="ghost">
            Clear
          </Button>
        )}
      </div>

      {/* Table */}
      {isLoading || isFetching ? (
        <div className="text-center py-12 text-gray-500">Loading posts...</div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <FileText className="h-12 w-12 mx-auto mb-3 opacity-40" />
          <p>No posts found</p>
        </div>
      ) : (
        <div className="overflow-x-auto border rounded-xl bg-white shadow-sm">
          <Table>
            <TableHeader className="bg-gray-50/80">
              <TableRow className="hover:bg-transparent">
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Author</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Content</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Classroom</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Comments</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.map((post: AdminPost) => (
                <TableRow key={post.id} className="hover:bg-gray-50/50 transition-colors">
                  <TableCell className="py-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-9 w-9 ring-2 ring-white shadow-sm">
                        <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white text-xs font-semibold">
                          {getInitials(post.author?.first_name, post.author?.last_name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium text-gray-900 text-sm">
                          {post.author ? `${post.author.first_name} ${post.author.last_name}` : "Deleted User"}
                        </div>
                        <div className="text-xs text-gray-500 capitalize">{post.author?.role || "—"}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="py-4 max-w-xs">
                    {post.text ? (
                      <p className="text-sm text-gray-700 line-clamp-2">{post.text}</p>
                    ) : post.image ? (
                      <span className="flex items-center gap-1 text-xs text-indigo-600 font-medium">
                        <ImageIcon className="h-3.5 w-3.5" /> Image post
                      </span>
                    ) : (
                      <span className="text-gray-400 text-xs italic">No text content</span>
                    )}
                  </TableCell>
                  <TableCell className="py-4 text-sm text-gray-600">
                    {post.classroom_name || <span className="text-gray-400">—</span>}
                  </TableCell>
                  <TableCell className="py-4 text-center">
                    <span className="inline-flex items-center gap-1 text-sm text-gray-600">
                      <MessageSquare className="h-3.5 w-3.5" />
                      {post.comment_count}
                    </span>
                  </TableCell>
                  <TableCell className="py-4 text-sm text-gray-500">{formatDate(post.created_at)}</TableCell>
                  <TableCell className="py-4 text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-500 hover:text-red-600 hover:bg-red-50"
                      onClick={() => setDeleteTarget(post.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination className="mt-4">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className={page === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
              />
            </PaginationItem>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <PaginationItem key={p}>
                <PaginationLink isActive={page === p} onClick={() => setPage(p)} className="cursor-pointer">
                  {p}
                </PaginationLink>
              </PaginationItem>
            ))}
            <PaginationItem>
              <PaginationNext
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className={page === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}

      <DeleteDialog
        open={!!deleteTarget}
        label="Post"
        deleting={deleting}
        onConfirm={handleDelete}
        onClose={() => setDeleteTarget(null)}
      />
    </div>
  );
};

// ─── Comments Tab ─────────────────────────────────────────────────
const CommentsTab = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const { data, isLoading, isFetching } = useGetAdminCommentsQuery({ page, search });
  const [deleteComment, { isLoading: deleting }] = useDeleteAdminCommentMutation();

  const comments = data?.results || [];
  const totalPages = Math.ceil((data?.count || 0) / 10);

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(1);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteComment(deleteTarget).unwrap();
      toast.success("Comment deleted successfully");
      setDeleteTarget(null);
    } catch {
      toast.error("Failed to delete comment");
    }
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search by author or comment text..."
            className="pl-9"
          />
        </div>
        <Button onClick={handleSearch} variant="outline">Search</Button>
        {search && (
          <Button onClick={() => { setSearch(""); setSearchInput(""); setPage(1); }} variant="ghost">
            Clear
          </Button>
        )}
      </div>

      {/* Table */}
      {isLoading || isFetching ? (
        <div className="text-center py-12 text-gray-500">Loading comments...</div>
      ) : comments.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-40" />
          <p>No comments found</p>
        </div>
      ) : (
        <div className="overflow-x-auto border rounded-xl bg-white shadow-sm">
          <Table>
            <TableHeader className="bg-gray-50/80">
              <TableRow className="hover:bg-transparent">
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Author</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Comment</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">On Post</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</TableHead>
                <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {comments.map((comment: AdminComment) => (
                <TableRow key={comment.id} className="hover:bg-gray-50/50 transition-colors">
                  <TableCell className="py-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-9 w-9 ring-2 ring-white shadow-sm">
                        <AvatarFallback className="bg-gradient-to-br from-teal-500 to-indigo-600 text-white text-xs font-semibold">
                          {getInitials(comment.author?.first_name, comment.author?.last_name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium text-gray-900 text-sm">
                          {comment.author ? `${comment.author.first_name} ${comment.author.last_name}` : "Deleted User"}
                        </div>
                        <div className="text-xs text-gray-500 capitalize">{comment.author?.role || "—"}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="py-4 max-w-xs">
                    {comment.text ? (
                      <p className="text-sm text-gray-700 line-clamp-2">{comment.text}</p>
                    ) : comment.image ? (
                      <span className="flex items-center gap-1 text-xs text-indigo-600 font-medium">
                        <ImageIcon className="h-3.5 w-3.5" /> Image comment
                      </span>
                    ) : (
                      <span className="text-gray-400 text-xs italic">No text</span>
                    )}
                  </TableCell>
                  <TableCell className="py-4 max-w-xs">
                    {comment.post_text ? (
                      <p className="text-xs text-gray-500 line-clamp-2 bg-gray-50 px-2 py-1 rounded border">
                        "{comment.post_text}"
                      </p>
                    ) : (
                      <span className="text-gray-400 text-xs">Image/video post</span>
                    )}
                  </TableCell>
                  <TableCell className="py-4 text-sm text-gray-500">{formatDate(comment.created_at)}</TableCell>
                  <TableCell className="py-4 text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-500 hover:text-red-600 hover:bg-red-50"
                      onClick={() => setDeleteTarget(comment.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination className="mt-4">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className={page === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
              />
            </PaginationItem>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <PaginationItem key={p}>
                <PaginationLink isActive={page === p} onClick={() => setPage(p)} className="cursor-pointer">
                  {p}
                </PaginationLink>
              </PaginationItem>
            ))}
            <PaginationItem>
              <PaginationNext
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className={page === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}

      <DeleteDialog
        open={!!deleteTarget}
        label="Comment"
        deleting={deleting}
        onConfirm={handleDelete}
        onClose={() => setDeleteTarget(null)}
      />
    </div>
  );
};

// ─── Main Component ──────────────────────────────────────────────
const ContentModeration = () => {
  return (
    <div className="bg-white rounded-xl border shadow-sm p-6 space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Content Moderation</h2>
        <p className="text-sm text-gray-500 mt-1">Review and delete inappropriate posts and comments from all users.</p>
      </div>

      <Tabs defaultValue="posts">
        <TabsList className="bg-gray-100">
          <TabsTrigger value="posts" className="gap-2">
            <FileText className="h-4 w-4" /> Posts
          </TabsTrigger>
          <TabsTrigger value="comments" className="gap-2">
            <MessageSquare className="h-4 w-4" /> Comments
          </TabsTrigger>
        </TabsList>

        <TabsContent value="posts" className="mt-6">
          <PostsTab />
        </TabsContent>

        <TabsContent value="comments" className="mt-6">
          <CommentsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContentModeration;
