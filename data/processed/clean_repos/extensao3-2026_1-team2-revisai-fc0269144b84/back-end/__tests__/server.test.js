'use strict';

const request = require('supertest');

// ── Mock heavy dependencies before requiring server ──────────────────────────

// Firestore fluent mock
const mockDoc = {
  exists: true,
  id: 'doc-id',
  data: () => ({ topic: 'Test', html: '<p>x</p>', createdAt: '2024-01-01T00:00:00.000Z', question: 'Q?', answer: 'A', themeName: 'T', termsCount: 2 }),
};
const mockDocRef = {
  get: jest.fn().mockResolvedValue(mockDoc),
  update: jest.fn().mockResolvedValue({}),
  delete: jest.fn().mockResolvedValue({}),
};
const mockCollectionRef = {
  orderBy: jest.fn().mockReturnThis(),
  add: jest.fn().mockResolvedValue({ id: 'new-doc-id' }),
  doc: jest.fn().mockReturnValue(mockDocRef),
  get: jest.fn().mockResolvedValue({
    docs: [{ id: 'doc-id', data: () => mockDoc.data() }],
  }),
};

jest.mock('../firebaseAdmin', () => ({
  db: { collection: jest.fn().mockReturnValue(mockCollectionRef) },
  admin: {},
}));

jest.mock('dotenv', () => ({ config: jest.fn() }));

jest.mock('@aws-sdk/client-lambda', () => ({
  LambdaClient: jest.fn().mockImplementation(() => ({ send: jest.fn() })),
  InvokeCommand: jest.fn(),
}));

const app = require('../server');

beforeEach(() => {
  jest.clearAllMocks();
  mockCollectionRef.orderBy.mockReturnThis();
  mockCollectionRef.add.mockResolvedValue({ id: 'new-doc-id' });
  mockCollectionRef.doc.mockReturnValue(mockDocRef);
  mockCollectionRef.get.mockResolvedValue({ docs: [{ id: 'doc-id', data: () => mockDoc.data() }] });
  mockDocRef.get.mockResolvedValue(mockDoc);
  mockDocRef.update.mockResolvedValue({});
  mockDocRef.delete.mockResolvedValue({});
});

// ── Flashcards ───────────────────────────────────────────────────────────────

describe('GET /api/flashcards', () => {
  it('returns 200 with flashcard array', async () => {
    const res = await request(app).get('/api/flashcards');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/flashcards', () => {
  it('returns 400 when required fields missing', async () => {
    const res = await request(app).post('/api/flashcards').send({ question: 'Q?' }); // missing answer
    expect(res.status).toBe(400);
  });

  it('returns 201 with saved flashcard', async () => {
    const res = await request(app)
      .post('/api/flashcards')
      .send({ question: 'Q?', answer: 'A', themeName: 'T' });
    expect(res.status).toBe(201);
    expect(res.body.id).toBe('new-doc-id');
  });
});

describe('PUT /api/flashcards/:id', () => {
  it('returns 400 when no fields provided', async () => {
    const res = await request(app).put('/api/flashcards/some-id').send({});
    expect(res.status).toBe(400);
  });

  it('returns 404 when flashcard not found', async () => {
    mockDocRef.get.mockResolvedValueOnce({ exists: false });
    const res = await request(app).put('/api/flashcards/bad-id').send({ question: 'New Q?' });
    expect(res.status).toBe(404);
  });

  it('returns 200 and updates flashcard', async () => {
    const res = await request(app).put('/api/flashcards/doc-id').send({ question: 'New Q?', themeName: 'New Theme' });
    expect(res.status).toBe(200);
    expect(mockDocRef.update).toHaveBeenCalledWith(expect.objectContaining({ question: 'New Q?', themeName: 'New Theme' }));
  });
});

describe('DELETE /api/flashcards/:id', () => {
  it('returns 200 on successful deletion', async () => {
    const res = await request(app).delete('/api/flashcards/doc-id');
    expect(res.status).toBe(200);
    expect(mockDocRef.delete).toHaveBeenCalled();
  });
});

// ── Resumos ──────────────────────────────────────────────────────────────────

describe('GET /api/resumos', () => {
  it('returns 200 with resumos array', async () => {
    const res = await request(app).get('/api/resumos');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/resumos', () => {
  it('returns 400 when fields missing', async () => {
    const res = await request(app).post('/api/resumos').send({ topic: 'T' }); // missing html
    expect(res.status).toBe(400);
  });

  it('returns 201 with saved resumo', async () => {
    const res = await request(app)
      .post('/api/resumos')
      .send({ topic: 'Fotossíntese', html: '<p>...</p>' });
    expect(res.status).toBe(201);
    expect(res.body.id).toBe('new-doc-id');
  });
});

describe('PUT /api/resumos/:id', () => {
  it('returns 400 when topic missing', async () => {
    const res = await request(app).put('/api/resumos/r-1').send({});
    expect(res.status).toBe(400);
  });

  it('returns 200 on successful update', async () => {
    const res = await request(app).put('/api/resumos/doc-id').send({ topic: 'New Topic' });
    expect(res.status).toBe(200);
    expect(mockDocRef.update).toHaveBeenCalledWith(expect.objectContaining({ topic: 'New Topic' }));
  });
});

describe('DELETE /api/resumos/:id', () => {
  it('returns 200 on successful deletion', async () => {
    const res = await request(app).delete('/api/resumos/doc-id');
    expect(res.status).toBe(200);
  });
});

// ── Dicionários ──────────────────────────────────────────────────────────────

describe('GET /api/dicionarios', () => {
  it('returns 200 with dicionarios array', async () => {
    const res = await request(app).get('/api/dicionarios');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/dicionarios', () => {
  it('returns 400 when fields missing', async () => {
    const res = await request(app).post('/api/dicionarios').send({ topic: 'D' }); // missing html
    expect(res.status).toBe(400);
  });

  it('returns 201 with saved dicionario', async () => {
    const res = await request(app)
      .post('/api/dicionarios')
      .send({ topic: 'Química', html: '<table/>', termsCount: 5 });
    expect(res.status).toBe(201);
    expect(res.body.id).toBe('new-doc-id');
  });
});

describe('PUT /api/dicionarios/:id', () => {
  it('returns 200 on successful update', async () => {
    const res = await request(app).put('/api/dicionarios/doc-id').send({ topic: 'Nova Química' });
    expect(res.status).toBe(200);
  });
});

describe('DELETE /api/dicionarios/:id', () => {
  it('returns 200 on successful deletion', async () => {
    const res = await request(app).delete('/api/dicionarios/doc-id');
    expect(res.status).toBe(200);
  });
});
