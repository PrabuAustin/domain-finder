from typing import List, Optional, Sequence

from fastapi import FastAPI
from pydantic import BaseModel

from .generator import generate_candidates, DEFAULT_TLDS
from .clients import domainr_prefilter, godaddy_find_available

app = FastAPI(title="Domain Finder API", version="1.0.0")


class GenerateRequest(BaseModel):
	concept: str
	tlds: Optional[List[str]] = None  # explicit override
	add_tlds: Optional[List[str]] = None  # extend
	remove_tlds: Optional[List[str]] = None  # subtract
	extras: Optional[List[str]] = None
	max_per_pattern: int = 50


class GenerateResponse(BaseModel):
	candidates: List[str]


class CheckRequest(BaseModel):
	domains: List[str]
	check_type: str = "FAST"


class CheckResponse(BaseModel):
	available: List[str]
	unavailable: List[str]


class FindRequest(BaseModel):
	concept: str
	tlds: Optional[List[str]] = None
	add_tlds: Optional[List[str]] = None
	remove_tlds: Optional[List[str]] = None
	extras: Optional[List[str]] = None
	check_type: str = "FAST"
	use_domainr_prefilter: bool = False
	max_per_pattern: int = 50


class FindResponse(BaseModel):
	available: List[str]
	unavailable: List[str]


def _resolve_tlds(tlds: Optional[List[str]], add_tlds: Optional[List[str]], remove_tlds: Optional[List[str]]) -> List[str]:
	res: List[str] = list(tlds) if tlds else list(DEFAULT_TLDS)
	if add_tlds:
		for t in add_tlds:
			if t not in res:
				res.append(t)
	if remove_tlds:
		res = [t for t in res if t not in set(remove_tlds)]
	return res


@app.get("/health")
async def health() -> dict:
	return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
	tlds = _resolve_tlds(req.tlds, req.add_tlds, req.remove_tlds)
	candidates = generate_candidates(
		concept=req.concept,
		tlds=tlds,
		extras=req.extras,
		max_per_pattern=req.max_per_pattern,
	)
	return GenerateResponse(candidates=candidates)


@app.post("/check", response_model=CheckResponse)
async def check(req: CheckRequest) -> CheckResponse:
	available = godaddy_find_available(req.domains, check_type=req.check_type)
	available_set = set(available)
	unavailable = [d for d in req.domains if d not in available_set]
	return CheckResponse(available=available, unavailable=unavailable)


@app.post("/find", response_model=FindResponse)
async def find(req: FindRequest) -> FindResponse:
	tlds = _resolve_tlds(req.tlds, req.add_tlds, req.remove_tlds)
	candidates = generate_candidates(
		concept=req.concept,
		tlds=tlds,
		extras=req.extras,
		max_per_pattern=req.max_per_pattern,
	)
	to_check: Sequence[str] = candidates
	if req.use_domainr_prefilter:
		to_check = domainr_prefilter(candidates)

	available = godaddy_find_available(to_check, check_type=req.check_type)
	available_set = set(available)
	unavailable = [d for d in to_check if d not in available_set]
	return FindResponse(available=available, unavailable=unavailable)
