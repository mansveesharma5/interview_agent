import './ResumeCard.css';

export default function ResumeCard({

  fileName,
}) {

  return (

    <div className="resume-card">

      <div className="resume-icon">
        📄
      </div>

      <div className="resume-info">

        <h4>{fileName}</h4>

        <p>
          Resume Uploaded Successfully ✅
        </p>

      </div>

    </div>
  );
}