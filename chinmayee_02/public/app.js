const form=document.getElementById('form'), error=document.getElementById('error'), result=document.getElementById('result');
form.addEventListener('submit',e=>{
 e.preventDefault(); error.textContent=''; result.classList.add('hidden');
 const age=Number(document.getElementById('age').value), weight=Number(document.getElementById('weight').value), height=Number(document.getElementById('height').value);
 if(!Number.isFinite(age)||age<1||age>120||!Number.isFinite(weight)||weight<=0||!Number.isFinite(height)||height<=0){error.textContent='Please enter valid age, weight and height.';return;}
 const bmi=weight/Math.pow(height/100,2); let category, explanation;
 if(age<18){category='Age-specific interpretation needed';explanation='For people under 18, BMI should be interpreted using age- and sex-specific growth charts.';}
 else if(bmi<18.5){category='Underweight range';explanation='Below the standard adult BMI screening range.';}
 else if(bmi<25){category='Healthy weight range';explanation='Within the standard adult BMI screening range.';}
 else if(bmi<30){category='Overweight range';explanation='Above the standard adult BMI screening range.';}
 else{category='Obesity range';explanation='Within the obesity range of standard adult BMI screening categories.';}
 document.getElementById('value').textContent=bmi.toFixed(1); document.getElementById('category').textContent=category; document.getElementById('explanation').textContent=explanation; result.classList.remove('hidden');
});
