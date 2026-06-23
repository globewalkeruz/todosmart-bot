import { useState } from 'react';
import { motion } from 'framer-motion';
import CategoryForm from '../components/CategoryForm';
import { SkeletonCard } from '../components/Skeleton';
import { useCategories, useDeleteCategory } from '../hooks/useCategories';
import { haptic } from '../lib/tg';
import { useStore } from '../store';
import type { Category } from '../types';

export default function Categories() {
  const { categorySheet, openCategorySheet } = useStore();
  const { data: categories = [], isLoading } = useCategories();
  const deleteCategory = useDeleteCategory();
  const [editing, setEditing] = useState<Category | undefined>();

  function handleEdit(cat: Category) {
    haptic('tap');
    setEditing(cat);
    openCategorySheet(cat.id);
  }

  function handleAdd() {
    haptic('tap');
    setEditing(undefined);
    openCategorySheet();
  }

  function handleDelete(cat: Category) {
    haptic('warning');
    if (confirm(`Delete "${cat.name}"? Todos in this category will lose their category.`)) {
      deleteCategory.mutate(cat.id);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Categories</h1>
        <p className="page-subtitle">Organise your todos into lists</p>
      </div>

      {isLoading ? (
        <div className="cat-grid">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} height={120} />
          ))}
        </div>
      ) : (
        <motion.div
          className="cat-grid"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {categories.map((cat, i) => (
            <motion.div
              key={cat.id}
              className="card cat-card"
              style={{
                background: `linear-gradient(135deg, ${cat.color}55 0%, ${cat.color}22 100%)`,
                border: `1px solid ${cat.color}60`,
              }}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
            >
              {/* Actions */}
              <div className="cat-card-actions">
                <button
                  className="cat-action-btn"
                  onClick={() => handleEdit(cat)}
                  aria-label="Edit"
                >
                  ✏️
                </button>
                <button
                  className="cat-action-btn"
                  onClick={() => handleDelete(cat)}
                  aria-label="Delete"
                >
                  🗑️
                </button>
              </div>

              <div className="cat-card-icon">{cat.icon}</div>
              <div className="cat-card-name">{cat.name}</div>
              <div className="cat-card-count">
                {cat.todo_count ?? 0} active todo{cat.todo_count !== 1 ? 's' : ''}
              </div>
            </motion.div>
          ))}

          {/* Add new */}
          <button className="cat-add-card" onClick={handleAdd} aria-label="Add category">
            <span className="cat-add-icon">+</span>
            <span className="cat-add-label">New List</span>
          </button>
        </motion.div>
      )}

      {categories.length === 0 && !isLoading && (
        <div className="empty-state">
          <div className="empty-state-icon">🗂️</div>
          <h3>No categories yet</h3>
          <p>Create categories to organise your todos.</p>
        </div>
      )}

      <CategoryForm editing={categorySheet.categoryId ? editing : undefined} />
    </div>
  );
}
