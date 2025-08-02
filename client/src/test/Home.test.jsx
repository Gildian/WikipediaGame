import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Home from '../views/Home/index.jsx'

// Mock fetch for API calls
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('Home Component', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('renders the main heading', () => {
    render(<Home />)
    expect(screen.getByText('Wikipedia Path Finder')).toBeInTheDocument()
  })

  it('renders input fields for start and goal articles', () => {
    render(<Home />)
    expect(screen.getByLabelText(/start article/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/goal article/i)).toBeInTheDocument()
  })

  it('renders algorithm selection dropdown', () => {
    render(<Home />)
    expect(screen.getByLabelText(/algorithm/i)).toBeInTheDocument()
    expect(screen.getByDisplayValue('Best-First Search')).toBeInTheDocument()
  })

  it('renders find path button', () => {
    render(<Home />)
    expect(screen.getByRole('button', { name: /find path/i })).toBeInTheDocument()
  })

  it('renders random articles button', () => {
    render(<Home />)
    expect(screen.getByRole('button', { name: /random articles/i })).toBeInTheDocument()
  })

  it('disables find path button when inputs are empty', () => {
    render(<Home />)
    const findButton = screen.getByRole('button', { name: /find path/i })
    expect(findButton).toBeDisabled()
  })

  it('enables find path button when both inputs have values', async () => {
    render(<Home />)
    const user = userEvent.setup()
    
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    const findButton = screen.getByRole('button', { name: /find path/i })
    
    await user.type(startInput, 'Python')
    await user.type(goalInput, 'Machine Learning')
    
    expect(findButton).not.toBeDisabled()
  })

  it('updates algorithm selection', async () => {
    render(<Home />)
    const user = userEvent.setup()
    
    const algorithmSelect = screen.getByLabelText(/algorithm/i)
    await user.selectOptions(algorithmSelect, 'depth-first')
    
    expect(screen.getByDisplayValue('Depth-First Search')).toBeInTheDocument()
  })

  it('handles random articles button click', async () => {
    const mockRandomResponse = {
      ok: true,
      json: () => Promise.resolve({
        articles: [
          { title: 'Random Article 1' },
          { title: 'Random Article 2' }
        ]
      })
    }
    
    mockFetch.mockResolvedValueOnce(mockRandomResponse)
    
    render(<Home />)
    const user = userEvent.setup()
    
    const randomButton = screen.getByRole('button', { name: /random articles/i })
    await user.click(randomButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/random')
    })
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('Random Article 1')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Random Article 2')).toBeInTheDocument()
    })
  })

  it('handles search form submission', async () => {
    const mockSearchResponse = {
      ok: true,
      json: () => Promise.resolve({
        path: ['Python', 'Programming Language', 'Machine Learning'],
        stats: {
          runtime: 2.5,
          articlesChecked: 15,
          algorithm: 'best-first'
        }
      })
    }
    
    mockFetch.mockResolvedValueOnce(mockSearchResponse)
    
    render(<Home />)
    const user = userEvent.setup()
    
    // Fill in the form
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    const findButton = screen.getByRole('button', { name: /find path/i })
    
    await user.type(startInput, 'Python')
    await user.type(goalInput, 'Machine Learning')
    await user.click(findButton)
    
    // Check that loading state is shown
    expect(screen.getByText(/finding path/i)).toBeInTheDocument()
    
    // Check that API was called correctly
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start: 'Python',
          goal: 'Machine Learning',
          algorithm: 'best-first'
        })
      })
    })
    
    // Check that results are displayed
    await waitFor(() => {
      expect(screen.getByText('Path Found!')).toBeInTheDocument()
      expect(screen.getByText('Python')).toBeInTheDocument()
      expect(screen.getByText('Programming Language')).toBeInTheDocument()
      expect(screen.getByText('Machine Learning')).toBeInTheDocument()
    })
  })

  it('handles API error responses', async () => {
    const mockErrorResponse = {
      ok: false,
      status: 404,
      json: () => Promise.resolve({
        error: 'Article not found'
      })
    }
    
    mockFetch.mockResolvedValueOnce(mockErrorResponse)
    
    render(<Home />)
    const user = userEvent.setup()
    
    // Fill in the form
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    const findButton = screen.getByRole('button', { name: /find path/i })
    
    await user.type(startInput, 'Nonexistent Article')
    await user.type(goalInput, 'Another Nonexistent')
    await user.click(findButton)
    
    // Check that error is displayed
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
      expect(screen.getByText(/article not found/i)).toBeInTheDocument()
    })
  })

  it('handles network errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))
    
    render(<Home />)
    const user = userEvent.setup()
    
    // Fill in the form
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    const findButton = screen.getByRole('button', { name: /find path/i })
    
    await user.type(startInput, 'Python')
    await user.type(goalInput, 'Machine Learning')
    await user.click(findButton)
    
    // Check that error is displayed
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
      expect(screen.getByText(/failed to search/i)).toBeInTheDocument()
    })
  })

  it('displays loading state during search', async () => {
    // Mock a delayed response
    const mockResponse = new Promise(resolve => {
      setTimeout(() => resolve({
        ok: true,
        json: () => Promise.resolve({ path: ['A', 'B'] })
      }), 100)
    })
    
    mockFetch.mockReturnValueOnce(mockResponse)
    
    render(<Home />)
    const user = userEvent.setup()
    
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    const findButton = screen.getByRole('button', { name: /find path/i })
    
    await user.type(startInput, 'Python')
    await user.type(goalInput, 'Machine Learning')
    await user.click(findButton)
    
    // Check loading state
    expect(screen.getByText(/finding path/i)).toBeInTheDocument()
    expect(findButton).toBeDisabled()
    
    // Wait for completion
    await waitFor(() => {
      expect(screen.queryByText(/finding path/i)).not.toBeInTheDocument()
    }, { timeout: 200 })
  })

  it('validates input fields', async () => {
    render(<Home />)
    const user = userEvent.setup()
    
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    
    // Test that inputs accept text
    await user.type(startInput, 'Test Article')
    expect(startInput).toHaveValue('Test Article')
    
    await user.clear(startInput)
    await user.type(startInput, '   ')  // Whitespace only
    expect(startInput).toHaveValue('   ')
    
    // Find button should still be disabled for whitespace-only input
    await user.type(goalInput, 'Valid Goal')
    const findButton = screen.getByRole('button', { name: /find path/i })
    expect(findButton).toBeDisabled()
  })

  it('clears results when starting new search', async () => {
    // First search
    const mockResponse1 = {
      ok: true,
      json: () => Promise.resolve({
        path: ['A', 'B', 'C'],
        stats: { runtime: 1.5, articlesChecked: 10 }
      })
    }
    
    mockFetch.mockResolvedValueOnce(mockResponse1)
    
    render(<Home />)
    const user = userEvent.setup()
    
    const startInput = screen.getByLabelText(/start article/i)
    const goalInput = screen.getByLabelText(/goal article/i)
    const findButton = screen.getByRole('button', { name: /find path/i })
    
    await user.type(startInput, 'First Start')
    await user.type(goalInput, 'First Goal')
    await user.click(findButton)
    
    await waitFor(() => {
      expect(screen.getByText('Path Found!')).toBeInTheDocument()
    })
    
    // Second search
    const mockResponse2 = {
      ok: true,
      json: () => Promise.resolve({
        path: ['X', 'Y'],
        stats: { runtime: 0.8, articlesChecked: 5 }
      })
    }
    
    mockFetch.mockResolvedValueOnce(mockResponse2)
    
    await user.clear(startInput)
    await user.clear(goalInput)
    await user.type(startInput, 'Second Start')
    await user.type(goalInput, 'Second Goal')
    await user.click(findButton)
    
    // During loading, results should be cleared
    expect(screen.getByText(/finding path/i)).toBeInTheDocument()
    expect(screen.queryByText('Path Found!')).not.toBeInTheDocument()
  })
})
