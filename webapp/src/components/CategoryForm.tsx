import { useEffect, useState } from 'react';
import BottomSheet from './BottomSheet';
import { useCreateCategory, useUpdateCategory } from '../hooks/useCategories';
import { useStore } from '../store';

const PRESET_COLORS = [
  '#667eea', '#f093fb', '#4ade80', '#fbbf24',
  '#f87171', '#38bdf8', '#a78bfa', '#fb923c',
];

const PRESET_ICONS = [
  '📁', '💼', '🏠', '🎯', '📚', '💪', '🛒', '🎨',
  '🏋️', '✈️', '🎵', '💊', '🌿', '🍕', '💡', '🔧',
];

interface CategoryData {
  id?: string;
  name?: string;
  color?: string;
  icon?: string;
}

export default function CategoryForm({ editing }: { editing?: CategoryData }) {
  const { categorySheet, closeCategorySheet } = useStore();
  const createCat = useCreateCategory();
  const updateCat = useUpdateCategory();

  const [name, setName] = useState('');
  const [color, setColor] = useState(PRESET_COLORS[0]);
  const [icon, setIcon] = useState(PRESET_ICONS[0]);

  useEffect(() => {
    if (categorySheet.isOpen) {
      setName(editing?.name ?? '');
      setColor(editing?.color ?? PRESET_COLORS[0]);
      setIcon(editing?.icon ?? PRESET_ICONS[0]);
    }
  }, [categorySheet.isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    if (editing?.id) {
      await updateCat.mutateAsync({ id: editing.id, name: name.trim(), color, icon });
    } else {
      await createCat.mutateAsync({ name: name.trim(), color, icon });
    }
    closeCategorySheet();
  }

  const isPending = createCat.isPending || updateCat.isPending;

  return (
    <BottomSheet
      isOpen={categorySheet.isOpen}
      onClose={closeCategorySheet}
      title={editing?.id ? 'Edit Category' : 'New Category'}
    >
      <form onSubmit={handleSubmit}>
        {/* Preview */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '14px 16px',
            borderRadius: 'var(--r-sm)',
            background: `${color}25`,
            border: `1.5px solid ${color}60`,
            marginBottom: 20,
          }}
        >
          <span style={{ fontSize: 28 }}>{icon}</span>
          <span style={{ fontSize: 17, fontWeight: 700, color: 'var(--txt-primary)' }}>
            {name || 'Category name…'}
          </span>
        </div>

        {/* Name */}
        <div className="form-group">
          <label className="form-label">Name</label>
          <input
            className="form-input"
            placeholder="e.g. Work, Personal, Health…"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoFocus
            required
          />
        </div>

        {/* Color */}
        <div className="form-group">
          <label className="form-label">Color</label>
          <div className="color-grid">
            {PRESET_COLORS.map((c) => (
              <button
                key={c}
                type="button"
                className={`color-swatch${color === c ? ' active' : ''}`}
                style={{ background: c }}
                onClick={() => setColor(c)}
                aria-label={c}
              />
            ))}
          </div>
        </div>

        {/* Icon */}
        <div className="form-group">
          <label className="form-label">Icon</label>
          <div className="emoji-grid">
            {PRESET_ICONS.map((e) => (
              <button
                key={e}
                type="button"
                className={`emoji-btn${icon === e ? ' active' : ''}`}
                onClick={() => setIcon(e)}
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-full"
          disabled={isPending || !name.trim()}
          style={{ marginTop: 8 }}
        >
          {isPending ? '⏳ Saving…' : editing?.id ? '💾 Save' : '✅ Create'}
        </button>
      </form>
    </BottomSheet>
  );
}
