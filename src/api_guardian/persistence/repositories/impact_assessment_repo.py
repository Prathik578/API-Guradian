"""SQLAlchemy implementation of ImpactAssessmentRepository."""

import uuid

from sqlalchemy import select

from api_guardian.application.interfaces.repositories import ImpactAssessmentRepository
from api_guardian.domain import TenantContext
from api_guardian.domain.maintenance import EvidenceLevel, ImpactAssessment, ImpactClassification
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import ImpactAssessmentModel


class SQLImpactAssessmentRepository(ImpactAssessmentRepository):
    """SQLAlchemy implementation of ImpactAssessment repository."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def save(self, ctx: TenantContext, assessment: ImpactAssessment) -> ImpactAssessment:
        with self.db.get_tenant_session(ctx) as session:
            db_assessment = session.execute(
                select(ImpactAssessmentModel).where(
                    ImpactAssessmentModel.id == assessment.id,
                    ImpactAssessmentModel.organization_id == ctx.tenant_id,
                )
            ).scalar_one_or_none()

            if not db_assessment:
                db_assessment = ImpactAssessmentModel(
                    id=assessment.id,
                    organization_id=ctx.tenant_id,
                    case_id=assessment.case_id,
                    snapshot_id=assessment.snapshot_id,
                )
                session.add(db_assessment)

            db_assessment.classification = assessment.classification.value
            db_assessment.evidence_level = assessment.evidence_level.value
            db_assessment.affected_files = assessment.affected_files
            db_assessment.evidence_payload = assessment.evidence_payload
            
            session.commit()
            return assessment

    def get_by_case_id(self, ctx: TenantContext, case_id: uuid.UUID) -> ImpactAssessment | None:
        with self.db.get_tenant_session(ctx) as session:
            db_assessment = session.execute(
                select(ImpactAssessmentModel).where(
                    ImpactAssessmentModel.case_id == case_id,
                    ImpactAssessmentModel.organization_id == ctx.tenant_id,
                )
            ).scalar_one_or_none()

            if not db_assessment:
                return None

            return ImpactAssessment(
                id=db_assessment.id,
                case_id=db_assessment.case_id,
                snapshot_id=db_assessment.snapshot_id,
                classification=ImpactClassification(db_assessment.classification),
                evidence_level=EvidenceLevel(db_assessment.evidence_level),
                affected_files=db_assessment.affected_files,
                evidence_payload=db_assessment.evidence_payload,
            )
