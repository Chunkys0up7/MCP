import React, { useState, useRef } from 'react';
import { Box, List, ListItem, ListItemText, Accordion, AccordionSummary, AccordionDetails, Typography } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Input from '../../components/common/Input';

const categories = [
  {
    label: '⭐ Favorites',
    components: [],
  },
  {
    label: 'Recently Used',
    components: [],
  },
  {
    label: 'LLM Models',
    components: ['GPT-4', 'Claude 3', 'Llama 2'],
  },
  {
    label: 'Data Loaders',
    components: ['File Upload', 'API Fetcher', 'DB Connector'],
  },
  {
    label: 'Data Processors',
    components: ['Validator', 'Transformer', 'Cleaner'],
  },
  {
    label: 'Logic & Control',
    components: ['If/Else', 'Loop', 'Merge'],
  },
  {
    label: 'Outputs & Sinks',
    components: ['Display Text', 'Save to DB', 'API Call'],
  },
];

const Palette: React.FC = () => {
  const [search, setSearch] = useState('');
  const [focusedCategory, setFocusedCategory] = useState<number | null>(null);
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);
  const itemRefs = useRef<(HTMLDivElement | null)[][]>([]);

  // Keyboard navigation handler
  const handleKeyDown = (catIdx: number, compIdx: number, components: string[], e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const nextIdx = compIdx + 1 < components.length ? compIdx + 1 : 0;
      setFocusedCategory(catIdx);
      setFocusedIndex(nextIdx);
      itemRefs.current[catIdx]?.[nextIdx]?.focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const prevIdx = compIdx - 1 >= 0 ? compIdx - 1 : components.length - 1;
      setFocusedCategory(catIdx);
      setFocusedIndex(prevIdx);
      itemRefs.current[catIdx]?.[prevIdx]?.focus();
    } else if (e.key === 'Enter' || e.key === ' ') {
      // Simulate drag start (for accessibility, could trigger a callback or show a message)
      e.preventDefault();
      // Optionally: Announce drag start
    }
  };

  // Filtered categories/components (if search is used)
  const filteredCategories = categories.map(cat => ({
    ...cat,
    components: cat.components.filter(c => c.toLowerCase().includes(search.toLowerCase())),
  }));

  // Prepare refs
  itemRefs.current = filteredCategories.map(cat => cat.components.map(() => null));

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Component Palette</Typography>
      <Input
        placeholder="Search components..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        size="small"
      />
      <Box sx={{ mt: 2 }}>
        {filteredCategories.map((category, catIdx) => (
          <Accordion key={category.label} defaultExpanded={catIdx < 2}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">{category.label}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <List dense role="list" aria-label={category.label}>
                {category.components.map((component, compIdx) => (
                  <ListItem
                    key={component}
                    button
                    draggable
                    tabIndex={0}
                    aria-selected={focusedCategory === catIdx && focusedIndex === compIdx}
                    ref={el => { itemRefs.current[catIdx][compIdx] = el; }}
                    onKeyDown={e => handleKeyDown(catIdx, compIdx, category.components, e)}
                    sx={{
                      outline: (focusedCategory === catIdx && focusedIndex === compIdx) ? '2px solid #1976d2' : 'none',
                      outlineOffset: 2,
                    }}
                    onFocus={() => {
                      setFocusedCategory(catIdx);
                      setFocusedIndex(compIdx);
                    }}
                    onDragStart={e => {
                      e.dataTransfer.setData('application/reactflow', component);
                      e.dataTransfer.effectAllowed = 'move';
                    }}
                    role="listitem"
                    aria-label={component}
                  >
                    <ListItemText primary={component} />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </Box>
  );
};

export default Palette; 